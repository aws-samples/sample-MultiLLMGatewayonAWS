# Original: https://github.com/boto/botocore/blob/develop/botocore/eventstream.py

"""Binary Event Stream Encoding"""

from binascii import crc32
from struct import pack
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_PRELUDE_LENGTH = 12

UINT8_BYTE_FORMAT = '!B'
UINT16_BYTE_FORMAT = '!H'
UINT32_BYTE_FORMAT = '!I'

class EventStreamMessageEncoder:
    """Encodes messages in the AWS event stream wire format."""

    @staticmethod
    def encode(headers: dict, payload_dict: dict) -> bytes:
        """Encode a message in the AWS event stream wire format."""

        headers_bytes = b''
        for key, value in headers.items():
            name_bytes = key.encode('utf-8')
            value_bytes = value.encode('utf-8')
            header = (
                pack(UINT8_BYTE_FORMAT, len(name_bytes)) +
                name_bytes +
                pack(UINT8_BYTE_FORMAT, 7) +  # 7 = string
                pack(UINT16_BYTE_FORMAT, len(value_bytes)) +
                value_bytes
            )
            headers_bytes += header

        payload_bytes = json.dumps(payload_dict).encode('utf-8')

        headers_length = len(headers_bytes)
        total_length = _PRELUDE_LENGTH + headers_length + len(payload_bytes) + 4

        # Prelude CRC (CRC32 of first 8 bytes of the prelude)
        prelude_without_crc = pack(UINT32_BYTE_FORMAT, total_length) + pack(UINT32_BYTE_FORMAT, headers_length)
        prelude_crc = crc32(prelude_without_crc) & 0xFFFFFFFF
        prelude = prelude_without_crc + pack(UINT32_BYTE_FORMAT, prelude_crc)

        # Use prelude_crc as base to calc message_crc
        message_bytes = prelude[8:] + headers_bytes + payload_bytes
        initial_crc = prelude_crc
        message_crc = crc32(message_bytes, initial_crc) & 0xFFFFFFFF  # Add initial_crc

        message = (
            prelude +
            headers_bytes +
            payload_bytes +
            pack(UINT32_BYTE_FORMAT, message_crc)
        )

        logger.debug(f"Total length: {total_length}")
        logger.debug(f"Headers length: {headers_length}")
        logger.debug(f"Prelude CRC: 0x{prelude_crc:08x}")
        logger.debug(f"Message CRC: 0x{message_crc:08x}")
        logger.debug(f"Complete message (hex): {message.hex()}")

        return message