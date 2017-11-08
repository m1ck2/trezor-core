from trezor.crypto.hashlib import sha256
from common import *

from apps.wallet.sign_tx.writers import *
from trezor.messages.SignTx import SignTx
from trezor.messages import InputScriptType, FailureType


class Bip143Error(ValueError):
    pass


class Bip143:

    def __init__(self):
        self.h_prevouts = HashWriter(sha256)
        self.h_sequence = HashWriter(sha256)
        self.h_outputs = HashWriter(sha256)

    def add_prevouts(self, txi: TxInputType):
        write_bytes_rev(self.h_prevouts, txi.prev_hash)
        write_uint32(self.h_prevouts, txi.prev_index)

    def get_prevouts_hash(self) -> bytes:
        return get_tx_hash(self.h_prevouts, True)

    def add_sequence(self, txi: TxInputType):
        write_uint32(self.h_sequence, txi.sequence)

    def get_sequence_hash(self) -> bytes:
        return get_tx_hash(self.h_sequence, True)

    def add_output(self, txo_bin: TxOutputBinType):
        write_tx_output(self.h_outputs, txo_bin)

    def get_outputs_hash(self) -> bytes:
        return get_tx_hash(self.h_outputs, True)

    def preimage_hash(self, tx: SignTx, txi: TxInputType, pubkeyhash) -> bytes:
        h_preimage = HashWriter(sha256)

        write_uint32(h_preimage, tx.version)  # nVersion
        write_bytes(h_preimage, bytearray(self.get_prevouts_hash()))  # hashPrevouts
        write_bytes(h_preimage, bytearray(self.get_sequence_hash()))  # hashSequence
        write_bytes_rev(h_preimage, txi.prev_hash)  # outpoint
        write_uint32(h_preimage, txi.prev_index)  # outpoint

        script_code = self.derive_script_code(txi, pubkeyhash)
        write_varint(h_preimage, len(script_code))  # scriptCode length
        write_bytes(h_preimage, script_code)  # scriptCode

        write_uint64(h_preimage, txi.amount)  # amount
        write_uint32(h_preimage, txi.sequence)  # nSequence

        write_bytes(h_preimage, bytearray(self.get_outputs_hash()))  # hashOutputs
        write_uint32(h_preimage, tx.lock_time)  # nLockTime
        write_uint32(h_preimage, 0x00000001)  # nHashType  todo

        return get_tx_hash(h_preimage, True)

    # this not redeemScript nor scriptPubKey
    # for P2WPKH this is always 0x1976a914{20-byte-pubkey-hash}88ac
    def derive_script_code(self, txi: TxInputType, pubkeyhash: bytes) -> bytearray:
        if txi.script_type == InputScriptType.SPENDP2SHWITNESS:
            s = bytearray(25)
            s[0] = 0x76  # OP_DUP
            s[1] = 0xA9  # OP_HASH_160
            s[2] = 0x14  # pushing 20 bytes
            s[3:23] = pubkeyhash
            s[23] = 0x88  # OP_EQUALVERIFY
            s[24] = 0xAC  # OP_CHECKSIG
            return s
        else:
            raise Bip143Error(FailureType.SyntaxError,
                              'Unknown input script type for bip143 script code')
