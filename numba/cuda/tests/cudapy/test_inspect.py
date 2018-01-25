from __future__ import print_function, division, absolute_import
from numba import cuda, float64, intp
from numba.cuda.testing import unittest, SerialMixin
from numba.cuda.testing import skip_on_cudasim
from numba.utils import StringIO


@skip_on_cudasim('Simulator does not generate code to be inspected')
class TestInspect(SerialMixin, unittest.TestCase):
    def test_monotyped(self):
        @cuda.jit("(float32, int32)")
        def foo(x, y):
            pass

        file = StringIO()
        foo.inspect_types(file=file)
        typeanno = file.getvalue()
        # Function name in annotation
        self.assertIn("foo", typeanno)
        # Signature in annotation
        self.assertIn("(float32, int32)", typeanno)
        file.close()
        # Function name in LLVM
        self.assertIn("foo", foo.inspect_llvm())

        asm = foo.inspect_asm()

        # Function name in PTX
        self.assertIn("foo", asm)
        # NVVM inserted comments in PTX
        self.assertIn("Generated by NVIDIA NVVM Compiler", asm)

    def test_polytyped(self):
        @cuda.jit
        def foo(x, y):
            pass

        foo(1, 1)
        foo(1.2, 2.4)

        file = StringIO()
        foo.inspect_types(file=file)
        typeanno = file.getvalue()
        file.close()
        # Signature in annotation
        self.assertIn("({0}, {0})".format(intp), typeanno)
        self.assertIn("(float64, float64)", typeanno)

        # Signature in LLVM dict
        llvmirs = foo.inspect_llvm()
        self.assertEqual(2, len(llvmirs), )
        self.assertIn((intp, intp), llvmirs)
        self.assertIn((float64, float64), llvmirs)

        # Function name in LLVM
        self.assertIn("foo", llvmirs[intp, intp])
        self.assertIn("foo", llvmirs[float64, float64])

        asmdict = foo.inspect_asm()

        # Signature in LLVM dict
        self.assertEqual(2, len(asmdict), )
        self.assertIn((intp, intp), asmdict)
        self.assertIn((float64, float64), asmdict)

        # NNVM inserted in PTX
        self.assertIn("foo", asmdict[intp, intp])
        self.assertIn("foo", asmdict[float64, float64])


if __name__ == '__main__':
    unittest.main()
