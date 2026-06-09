from renamer.rules.base import RenameRule, RuleResult
from renamer.rules.insert import InsertRule
from renamer.rules.delete import DeleteRule
from renamer.rules.remove import RemoveRule
from renamer.rules.replace import ReplaceRule
from renamer.rules.rearrange import RearrangeRule
from renamer.rules.extension import ExtensionRule
from renamer.rules.strip import StripRule
from renamer.rules.case import CaseRule
from renamer.rules.serialize import SerializeRule
from renamer.rules.randomize import RandomizeRule
from renamer.rules.padding import PaddingRule
from renamer.rules.cleanup import CleanUpRule
from renamer.rules.translit import TranslitRule
from renamer.rules.reformat_date import ReformatDateRule
from renamer.rules.regex_rule import RegexRule
from renamer.rules.user_input import UserInputRule
from renamer.rules.mapping import MappingRule

ALL_RULES = [
    InsertRule, DeleteRule, RemoveRule, ReplaceRule,
    RearrangeRule, ExtensionRule, StripRule, CaseRule,
    SerializeRule, RandomizeRule, PaddingRule, CleanUpRule,
    TranslitRule, ReformatDateRule, RegexRule, UserInputRule, MappingRule,
]
