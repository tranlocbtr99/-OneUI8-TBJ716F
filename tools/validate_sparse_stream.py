#!/usr/bin/env python3
"""Read-only streaming validation of Android sparse chunks."""
import struct

TYPES = {0xCAC1: 'raw', 0xCAC2: 'fill', 0xCAC3: 'dont_care', 0xCAC4: 'crc32'}

def read_exact(stream, n):
    data = stream.read(n)
    if len(data) != n:
        raise ValueError('truncated sparse stream')
    return data

def validate(stream, size):
    header = read_exact(stream, 28)
    magic, major, minor, fh, ch, block, blocks, chunks, checksum = struct.unpack('<IHHHHIIII', header)
    if magic != 0xED26FF3A or major != 1 or fh < 28 or ch < 12 or not 512 <= block <= 1048576 or block & (block-1) or not blocks or not chunks:
        raise ValueError('invalid sparse header')
    if fh > size or chunks > (size-fh)//ch:
        raise ValueError('impossible chunk count')
    read_exact(stream, fh-28)
    consumed, output_blocks = fh, 0
    counts = {v: 0 for v in TYPES.values()}
    for i in range(chunks):
        h = read_exact(stream, ch)
        kind, reserved, chunk_blocks, total_size = struct.unpack_from('<HHII', h)
        if kind not in TYPES or reserved or total_size < ch:
            raise ValueError('invalid chunk')
        name = TYPES[kind]
        if (name == 'crc32' and chunk_blocks) or (name != 'crc32' and not chunk_blocks):
            raise ValueError('invalid block count')
        payload = {'raw': chunk_blocks*block, 'fill': 4, 'dont_care': 0, 'crc32': 4}[name]
        if total_size != ch+payload or consumed+total_size > size:
            raise ValueError('invalid payload size')
        if output_blocks + chunk_blocks > blocks:
            raise ValueError('too many output blocks')
        remaining = payload
        while remaining:
            n = min(1048576, remaining)
            read_exact(stream, n)
            remaining -= n
        consumed += total_size
        output_blocks += chunk_blocks
        if output_blocks > blocks:
            raise ValueError('too many output blocks')
        counts[name] += 1
    if output_blocks != blocks or consumed != size:
        raise ValueError('output block mismatch or trailing bytes')
    return {'input_bytes': consumed, 'output_bytes': blocks*block, 'chunk_count': chunks, 'chunk_types': counts, 'structure_valid': True, 'checksum_verified': False}
