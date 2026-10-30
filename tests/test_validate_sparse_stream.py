import importlib.util
import io
import pathlib
import struct
import unittest

source=pathlib.Path(__file__).resolve().parents[1]/'tools'/'validate_sparse_stream.py'
spec=importlib.util.spec_from_file_location('sparse_validator',source)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def sparse(chunks, blocks):
    head=struct.pack('<IHHHHIIII',0xED26FF3A,1,0,28,12,4096,blocks,len(chunks),0)
    return head+b''.join(chunks)

def chunk(kind,blocks,payload=b''):
    return struct.pack('<HHII',kind,0,blocks,12+len(payload))+payload

class SparseValidationTests(unittest.TestCase):
    def check(self,data):
        return mod.validate(io.BytesIO(data),len(data))

    def test_raw(self):
        result=self.check(sparse([chunk(0xCAC1,1,b'A'*4096)],1))
        self.assertTrue(result['structure_valid'])
        self.assertEqual(result['output_bytes'],4096)

    def test_fill(self):
        self.assertEqual(self.check(sparse([chunk(0xCAC2,2,b'ABCD')],2))['chunk_types']['fill'],1)

    def test_dont_care(self):
        self.assertEqual(self.check(sparse([chunk(0xCAC3,3)],3))['output_bytes'],12288)

    def test_crc32(self):
        data=sparse([chunk(0xCAC3,1),chunk(0xCAC4,0,b'1234')],1)
        self.assertEqual(self.check(data)['chunk_types']['crc32'],1)

    def test_truncated_raw(self):
        data=sparse([chunk(0xCAC1,1,b'A'*4096)],1)
        with self.assertRaises(ValueError):
            self.check(data[:-1])

    def test_wrong_payload_size(self):
        with self.assertRaises(ValueError):
            self.check(sparse([chunk(0xCAC1,1,b'A')],1))

    def test_output_overflow(self):
        with self.assertRaises(ValueError):
            self.check(sparse([chunk(0xCAC3,2)],1))

    def test_trailing_bytes(self):
        with self.assertRaises(ValueError):
            self.check(sparse([chunk(0xCAC3,1)],1)+b'X')

if __name__=='__main__':
    unittest.main()
