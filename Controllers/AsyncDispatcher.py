"""Maps OSC addresses to handler functions
   Updated to Async functionality for Trio by @pycepticus 2023
"""

import collections
import logging
import re
import time
from pythonosc import osc_packet
from typing import overload, List, Union, Any, Generator, Tuple, Callable, Optional, DefaultDict
from pythonosc.osc_message import OscMessage
from pythonosc.dispatcher import Dispatcher, Handler


class AsyncHandler(Handler):
    async def invoke(self, client_address: Tuple[str, int], message: OscMessage) -> None:
        """Invokes the associated callback function

        Args:
            client_address: Address match that causes the invocation
            message: Message causing invocation
       """
        if self.needs_reply_address:
            if self.args:
                await self.callback(client_address, message.address, self.args, *message)
            else:
                await self.callback(client_address, message.address, *message)
        else:
            if self.args:
                await self.callback(message.address, self.args, *message)
            else:
                await self.callback(message.address, *message)


class AsyncDispatcher(Dispatcher):
    def map(self, address: str, handler: Callable, *args: Union[Any, List[Any]],
            needs_reply_address: bool = False) -> AsyncHandler:
        """Map an address to a handler

        The callback function must have one of the following signatures:

        ``def some_cb(address: str, *osc_args: List[Any]) -> None:``
        ``def some_cb(address: str, fixed_args: List[Any], *osc_args: List[Any]) -> None:``

        ``def some_cb(client_address: Tuple[str, int], address: str, *osc_args: List[Any]) -> None:``
        ``def some_cb(client_address: Tuple[str, int], address: str, fixed_args: List[Any], *osc_args: List[Any]) -> None:``

        Args:
            address: Address to be mapped
            handler: Callback function that will be called as the handler for the given address
            *args: Fixed arguements that will be passed to the callback function
            needs_reply_address: Whether the IP address from which the message originated from shall be passed as
                an argument to the handler callback

        Returns:
            The handler object that will be invoked should the given address match

        """
        # TODO: Check the spec:
        # http://opensoundcontrol.org/spec-1_0
        # regarding multiple mappings
        handlerobj = AsyncHandler(handler, list(args), needs_reply_address)
        self._map[address].append(handlerobj)
        return handlerobj
    
    @overload
    def unmap(self, address: str, handler: AsyncHandler) -> None:
        """Remove an already mapped handler from an address

        Args:
            address (str): Address to be unmapped
            handler (AsyncHandler): A AsyncHandler object as returned from map().
        """
        pass

    @overload
    def unmap(self, address: str, handler: Callable, *args: Union[Any, List[Any]],
              needs_reply_address: bool = False) -> None:
        """Remove an already mapped handler from an address

        Args:
            address: Address to be unmapped
            handler: A function that will be run when the address matches with
                the OscMessage passed as parameter.
            args: Any additional arguments that will be always passed to the
                handlers after the osc messages arguments if any.
            needs_reply_address: True if the handler function needs the
                originating client address passed (as the first argument).
        """
        pass

    def unmap(self, address, handler, *args, needs_reply_address=False):
        try:
            if isinstance(handler, AsyncHandler):
                self._map[address].remove(handler)
            else:
                self._map[address].remove(AsyncHandler(handler, list(args), needs_reply_address))
        except ValueError as e:
            if str(e) == "list.remove(x): x not in list":
                raise ValueError("Address '%s' doesn't have handler '%s' mapped to it" % (address, handler)) from e
    
    def handlers_for_address(self, address_pattern: str) -> Generator[AsyncHandler, None, None]:
        """Yields handlers matching an address


        Args:
            address_pattern: Address to match

        Returns:
            Generator yielding AsyncHandlers matching address_pattern
        """
        # First convert the address_pattern into a matchable regexp.
        # '?' in the OSC Address Pattern matches any single character.
        # Let's consider numbers and _ "characters" too here, it's not said
        # explicitly in the specification but it sounds good.
        escaped_address_pattern = re.escape(address_pattern)
        pattern = escaped_address_pattern.replace('\\?', '\\w?')
        # '*' in the OSC Address Pattern matches any sequence of zero or more
        # characters.
        pattern = pattern.replace('\\*', '[\w|\+]*')
        # The rest of the syntax in the specification is like the re module so
        # we're fine.
        pattern = pattern + '$'
        patterncompiled = re.compile(pattern)
        matched = False

        for addr, handlers in self._map.items():
            if (patterncompiled.match(addr)
                    or (('*' in addr) and re.match(addr.replace('*', '[^/]*?/*'), address_pattern))):
                yield from handlers
                matched = True

        if not matched and self._default_handler:
            logging.debug('No handler matched but default handler present, added it.')
            yield self._default_handler
    
    async def call_handlers_for_packet(self, data: bytes, client_address: Tuple[str, int]) -> None:
        """Invoke handlers for all messages in OSC packet

        The incoming OSC Packet is decoded and the handlers for each included message is found and invoked.

        Args:
            data: Data of packet
            client_address: Address of client this packet originated from
        """

        # Get OSC messages from all bundles or standalone message.
        try:
            packet = osc_packet.OscPacket(data)
            for timed_msg in packet.messages:
                now = time.time()
                handlers = self.handlers_for_address(
                    timed_msg.message.address)
                if not handlers:
                    continue
                # If the message is to be handled later, then so be it.
                if timed_msg.time > now:
                    time.sleep(timed_msg.time - now)
                for handler in handlers:
                    await handler.invoke(client_address, timed_msg.message)
        except osc_packet.ParseError:
            pass

    def set_default_handler(self, handler: Callable, needs_reply_address: bool = False) -> None:
        """Sets the default handler

        The default handler is invoked every time no other handler is mapped to an address.

        Args:
            handler: Callback function to handle unmapped requests
            needs_reply_address: Whether the callback shall be passed the client address
        """
        self._default_handler = None if (handler is None) else AsyncHandler(handler, [], needs_reply_address)
