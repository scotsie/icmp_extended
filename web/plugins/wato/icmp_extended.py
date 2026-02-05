#!/usr/bin/env python3
"""
WATO plugin for icmp_extended active check

This file directly registers the icmp_extended ruleset by importing
the valuespec function from cmk_addons and registering it here.
"""

from cmk.utils.rulesets.definition import RuleGroup
from cmk.gui.plugins.wato.utils import HostRulespec, rulespec_registry
from cmk.gui.wato import RulespecGroupActiveChecks

# Import the valuespec function from our cmk_addons module
from cmk_addons.plugins.icmp_extended.rulesets.icmp import (
    _valuespec_active_checks_icmp,
)

# Register the ruleset in this scope (where load_web_plugins expects it)
rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupActiveChecks,
        match_type="all",
        name=RuleGroup.ActiveChecks("icmp"),
        valuespec=_valuespec_active_checks_icmp,
    )
)
