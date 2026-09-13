import os
import clang
from clang import cindex
from tokenizers import Tokenizer, normalizers, pre_tokenizers, processors
from tokenizers.models import BPE
from tokenizers.normalizers import StripAccents, Replace
from tokenizers.processors import TemplateProcessing
from tokenizers.pre_tokenizers import PreTokenizer

# Fix libclang DLL on Windows
dll_path = os.path.join(os.path.dirname(clang.__file__), "native", "libclang.dll")
if os.path.exists(dll_path):
    cindex.Config.set_library_file(dll_path)

class MyTokenizer:
    _cidx = None
    @property
    def cidx(self):
        if MyTokenizer._cidx is None:
            MyTokenizer._cidx = cindex.Index.create()
        return MyTokenizer._cidx

    def clang_split(self, i, normalized_string):
        tok = []
        tu = self.cidx.parse('tmp.c', args=[''], unsaved_files=[('tmp.c', str(normalized_string.original))], options=0)
        for t in tu.get_tokens(extent=tu.cursor.extent):
            spelling = t.spelling.strip()
            if spelling != '':
                tok.append(normalized_string.__class__(spelling))
        return tok

    def pre_tokenize(self, pretok):
        pretok.split(self.clang_split)

def load_custom_tokenizer(vocab_path, merges_path, max_length=1024):
    vocab, merges = BPE.read_file(vocab=vocab_path, merges=merges_path)
    tokenizer = Tokenizer(BPE(vocab, merges, unk_token="<unk>"))
    tokenizer.normalizer = normalizers.Sequence([StripAccents(), Replace(" ", "Ä")])
    tokenizer.pre_tokenizer = PreTokenizer.custom(MyTokenizer())
    tokenizer.post_processor = TemplateProcessing(
        single="<s> $A </s>",
        special_tokens=[("<s>",0), ("<pad>",1), ("</s>",2), ("<unk>",3), ("<mask>",4)]
    )
    tokenizer.enable_truncation(max_length=max_length)
    tokenizer.enable_padding(pad_id=1, pad_token='<pad>')
    return tokenizer
