#!/usr/bin/env python3

import argparse
import os
import unittest

from pytorch_translate import constants, preprocess
from pytorch_translate.data.dictionary import Dictionary
from pytorch_translate.test import utils as test_utils


class TestPreprocess(unittest.TestCase):
    def setUp(self):
        (
            self.source_text_file,
            self.target_text_file,
        ) = test_utils.create_test_text_files()

    def get_common_data_args_namespace(self):
        args = argparse.Namespace()

        args.train_source_text_file = self.source_text_file
        args.train_target_text_file = self.target_text_file
        args.eval_source_text_file = self.source_text_file
        args.eval_target_text_file = self.target_text_file

        # The idea is to have these filled in during preprocessing
        args.train_source_binary_path = ""
        args.train_target_binary_path = ""
        args.eval_source_binary_path = ""
        args.eval_target_binary_path = ""

        # Required data preprocessing args
        args.append_eos_to_source = False
        args.reverse_source = True
        args.fairseq_data_format = False

        args.multiling_source_lang = None  # Indicates no multilingual data
        args.penalized_target_tokens_file = ""

        args.source_vocab_file = test_utils.make_temp_file()
        args.source_max_vocab_size = None
        args.target_vocab_file = test_utils.make_temp_file()
        args.target_max_vocab_size = None
        args.char_source_vocab_file = ""
        args.char_target_vocab_file = ""

        args.task = "pytorch_translate"
        return args

    def test_build_vocabs_char(self):
        args = self.get_common_data_args_namespace()
        args.arch = "char_aware_hybrid"
        args.char_source_max_vocab_size = 30
        args.char_target_max_vocab_size = 30
        args.char_source_vocab_file = test_utils.make_temp_file()
        args.char_target_vocab_file = test_utils.make_temp_file()
        dictionaries = preprocess.build_vocabs(args, Dictionary)
        assert len(dictionaries["char_source_dict"]) > 0
        assert len(dictionaries["char_target_dict"]) > 0

    def test_build_vocabs_no_char(self):
        args = self.get_common_data_args_namespace()
        args.arch = "rnn"
        dictionaries = preprocess.build_vocabs(args, Dictionary)
        dictionaries["char_source_dict"] is None
        dictionaries["char_target_dict"] is None

    def test_preprocess(self):
        """
        This is just a correctness test to make sure no errors are thrown when
        all the required args are passed. Actual parsing code is tested by
        test_data.py
        """
        args = self.get_common_data_args_namespace()
        preprocess.preprocess_corpora(args)
        for file_type in (
            "train_source_binary_path",
            "train_target_binary_path",
            "eval_source_binary_path",
            "eval_target_binary_path",
        ):
            file = getattr(args, file_type)
            assert file and os.path.isfile(file)
            assert file.endswith(".npz")

    def test_preprocess_with_monolingual(self):
        """
        This is just a correctness test to make sure no errors are thrown when
        all the required args are passed. Actual parsing code is tested by
        test_data.py
        """
        args = self.get_common_data_args_namespace()
        args.task = constants.SEMI_SUPERVISED_TASK
        args.train_mono_source_text_file = self.source_text_file
        args.train_mono_target_text_file = self.target_text_file
        preprocess.preprocess_corpora(args)
        for file_type in (
            "train_source_binary_path",
            "train_target_binary_path",
            "eval_source_binary_path",
            "eval_target_binary_path",
            "train_mono_source_binary_path",
            "train_mono_target_binary_path",
        ):
            file_path = getattr(args, file_type)
            assert file_path and os.path.isfile(file_path)
            assert file_path.endswith(".npz")

    def test_preprocess_with_monolingual_with_tgt_chars(self):
        """
        This is just a correctness test to make sure no errors are thrown when
        all the required args are passed. Actual parsing code is tested by
        test_data.py
        """
        args = self.get_common_data_args_namespace()
        args.task = constants.SEMI_SUPERVISED_TASK
        args.train_mono_source_text_file = self.source_text_file
        args.train_mono_target_text_file = self.target_text_file
        args.arch = "char_aware_hybrid"
        args.char_source_max_vocab_size = 30
        args.char_target_max_vocab_size = 30
        args.char_source_vocab_file = test_utils.make_temp_file()
        args.char_target_vocab_file = test_utils.make_temp_file()

        preprocess.preprocess_corpora(args)
        for file_type in (
            "train_source_binary_path",
            "train_target_binary_path",
            "eval_source_binary_path",
            "eval_target_binary_path",
            "train_mono_source_binary_path",
            "train_mono_target_binary_path",
        ):
            file_path = getattr(args, file_type)
            assert file_path and os.path.isfile(file_path)
            assert file_path.endswith(".npz")
