"""
Websocket handler shims exposing legacy channel builders and decoders.
"""

from infrastructure.external.mexc_client.ws_channels import (
    BinaryDecoder,
    book_ticker_batch_stream,
    book_ticker_stream,
    build_protobuf_decoder,
    diff_depth_stream,
    kline_stream,
    mini_tickers_stream,
    partial_depth_stream,
    trade_stream,
)

__all__ = [
    "BinaryDecoder",
    "book_ticker_batch_stream",
    "book_ticker_stream",
    "build_protobuf_decoder",
    "diff_depth_stream",
    "kline_stream",
    "mini_tickers_stream",
    "partial_depth_stream",
    "trade_stream",
]
