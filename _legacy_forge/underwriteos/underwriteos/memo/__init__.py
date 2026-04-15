"""Memo generation — canonical Colony Bank loan report template + renderer."""
from .template import COLONY_BANK_SECTIONS, MemoSection, get_template
from .renderer import DealContext, render_memo, missing_required_sections
