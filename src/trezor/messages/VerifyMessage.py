# Automatically generated by pb2py
from protobuf import protobuf as p
t = p.MessageType()
t.add_field(1, 'address', p.UnicodeType)
t.add_field(2, 'signature', p.BytesType)
t.add_field(3, 'message', p.BytesType)
VerifyMessage = t
TYPE = const(39)