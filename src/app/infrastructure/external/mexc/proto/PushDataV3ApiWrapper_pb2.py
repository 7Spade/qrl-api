from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

# Import dependencies to register their descriptors in the default pool.
from . import (  # noqa: F401
    PrivateAccountV3Api_pb2,
    PrivateDealsV3Api_pb2,
    PrivateOrdersV3Api_pb2,
    PublicAggreBookTickerV3Api_pb2,
    PublicAggreDealsV3Api_pb2,
    PublicAggreDepthsV3Api_pb2,
    PublicBookTickerBatchV3Api_pb2,
    PublicBookTickerV3Api_pb2,
    PublicDealsV3Api_pb2,
    PublicIncreaseDepthsBatchV3Api_pb2,
    PublicIncreaseDepthsV3Api_pb2,
    PublicLimitDepthsV3Api_pb2,
    PublicMiniTickerV3Api_pb2,
    PublicMiniTickersV3Api_pb2,
    PublicSpotKlineV3Api_pb2,
)

_POOL = descriptor_pool.Default()


def _register_wrapper() -> None:
    file_proto = descriptor_pb2.FileDescriptorProto(
        name="PushDataV3ApiWrapper.proto",
        package="com.mxc.push.common.protobuf",
        syntax="proto3",
    )
    msg = file_proto.message_type.add()
    msg.name = "PushDataV3ApiWrapper"

    chan = msg.field.add()
    chan.name = "channel"
    chan.number = 1
    chan.label = 1  # LABEL_OPTIONAL
    chan.type = 9  # TYPE_STRING

    msg.oneof_decl.add().name = "body"
    for name, number, type_name in [
        ("publicDeals", 301, ".PublicDealsV3Api"),
        ("publicIncreaseDepths", 302, ".PublicIncreaseDepthsV3Api"),
        ("publicLimitDepths", 303, ".PublicLimitDepthsV3Api"),
        ("privateOrders", 304, ".PrivateOrdersV3Api"),
        ("publicBookTicker", 305, ".PublicBookTickerV3Api"),
        ("privateDeals", 306, ".PrivateDealsV3Api"),
        ("privateAccount", 307, ".PrivateAccountV3Api"),
        ("publicSpotKline", 308, ".PublicSpotKlineV3Api"),
        ("publicMiniTicker", 309, ".PublicMiniTickerV3Api"),
        ("publicMiniTickers", 310, ".PublicMiniTickersV3Api"),
        ("publicBookTickerBatch", 311, ".PublicBookTickerBatchV3Api"),
        ("publicIncreaseDepthsBatch", 312, ".PublicIncreaseDepthsBatchV3Api"),
        ("publicAggreDepths", 313, ".PublicAggreDepthsV3Api"),
        ("publicAggreDeals", 314, ".PublicAggreDealsV3Api"),
        ("publicAggreBookTicker", 315, ".PublicAggreBookTickerV3Api"),
    ]:
        f = msg.field.add()
        f.name = name
        f.number = number
        f.label = 1
        f.type = 11  # TYPE_MESSAGE
        f.type_name = type_name
        f.oneof_index = 0

    for name, number, type_enum in [
        ("symbol", 3, 9),
        ("symbolId", 4, 9),
        ("createTime", 5, 3),
        ("sendTime", 6, 3),
    ]:
        f = msg.field.add()
        f.name = name
        f.number = number
        f.label = 1
        f.type = type_enum

    _POOL.Add(file_proto)


_register_wrapper()
PushDataV3ApiWrapper = message_factory.GetMessageClass(
    _POOL.FindMessageTypeByName(
        "com.mxc.push.common.protobuf.PushDataV3ApiWrapper"
    )
)

__all__ = ["PushDataV3ApiWrapper"]
