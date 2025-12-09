#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="type-arg"


from cmk.gui.exceptions import MKUserError
from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import check_icmp_params, HostRulespec, rulespec_registry
from cmk.gui.valuespec import (
    CascadingDropdown,
    Checkbox,
    Dictionary,
    DictionaryEntry,
    Float,
    Hostname,
    Integer,
    TextInput,
    Tuple,
    ValueSpec,
)
from cmk.gui.wato import RulespecGroupActiveChecks
from cmk.utils.rulesets.definition import RuleGroup


def _validate_ip_index(value: int, varprefix: str) -> None:
    if value >= 1:
        return
    raise MKUserError(varprefix, _("The index must be greater or equal to 1."))


def _validate_mos_value(value: float, varprefix: str) -> None:
    if 0.0 <= value <= 4.4:
        return
    raise MKUserError(varprefix, _("MOS value must be between 0.0 and 4.4"))


def _valuespec_active_checks_icmp() -> ValueSpec:
    elements: list[DictionaryEntry] = [
        (
            "description",
            TextInput(
                title=_("Service description"),
                allow_empty=False,
                default_value="PING",
            ),
        ),
        (
            "address",
            CascadingDropdown(
                title=_("Alternative address to ping"),
                help=_(
                    "If you omit this setting then the configured IP address of that host "
                    "will be pinged. In the host configuration you can provide additional "
                    "addresses besides the main IP address (additional IP addresses section). "
                    "In this option you can select which set of addresses you want to include "
                    'for this check. "Ping additional IP addresses" will omit the host '
                    'configured main address while the "Ping all addresses" option will '
                    "include both the main and additional addresses."
                ),
                orientation="horizontal",
                choices=[
                    ("address", _("Ping the normal IP address")),
                    ("alias", _("Use the alias as DNS name / IP address")),
                    (
                        "explicit",
                        _("Ping the following explicit address / DNS name"),
                        Hostname(),
                    ),
                    ("all_ipv4addresses", _("Ping all IPv4 addresses")),
                    ("all_ipv6addresses", _("Ping all IPv6 addresses")),
                    ("additional_ipv4addresses", _("Ping additional IPv4 addresses")),
                    ("additional_ipv6addresses", _("Ping additional IPv6 addresses")),
                    (
                        "indexed_ipv4address",
                        _("Ping IPv4 address identified by its index (starting at 1)"),
                        Integer(default_value=1, validate=_validate_ip_index),
                    ),
                    (
                        "indexed_ipv6address",
                        _("Ping IPv6 address identified by its index (starting at 1)"),
                        Integer(default_value=1, validate=_validate_ip_index),
                    ),
                ],
            ),
        ),
        (
            "multiple_services",
            Checkbox(
                title=_("Multiple services"),
                label=_("Create a service for every pinged IP address"),
                default_value=False,
            ),
        ),
        (
            "min_pings",
            Integer(
                title=_("Number of positive responses required for OK state"),
                help=_(
                    "When pinging multiple addresses, failure to ping one of the "
                    "provided addresses will lead to a Crit status of the service. "
                    "This option allows to specify the minimum number of successful "
                    "pings which will still classify the service as OK. The smallest "
                    "number is 1 and the maximum number should be (number of addresses - 1). "
                    "A number larger than the suggested number will always lead to a "
                    "Crit Status. One must also select a suitable option from the "
                    '"Alternative address to ping" above.'
                ),
                minvalue=1,
            ),
        ),
        # Jitter thresholds
        (
            "jitter",
            Tuple(
                title=_("Jitter thresholds"),
                help=_(
                    "Jitter is the variation in round trip time between packets. "
                    "This measures network stability and is important for VoIP and real-time applications. "
                    "Thresholds are specified in milliseconds. "
                    "Good jitter: < 30ms, Acceptable: 30-50ms, Poor: > 50ms"
                ),
                elements=[
                    Float(
                        title=_("Warning at"),
                        unit=_("ms"),
                        default_value=40.0,
                        minvalue=0.0,
                    ),
                    Float(
                        title=_("Critical at"),
                        unit=_("ms"),
                        default_value=80.0,
                        minvalue=0.0,
                    ),
                ],
            ),
        ),
        # NEW: MOS thresholds
        (
            "mos",
            Tuple(
                title=_("Mean Opinion Score (MOS) thresholds"),
                help=_(
                    "MOS (Mean Opinion Score) is a numerical measure of voice call quality "
                    "ranging from 1.0 (bad) to 4.4 (excellent). It combines latency, jitter, "
                    "and packet loss into a single quality metric. "
                    "<br><br>"
                    "<b>MOS Score Guide:</b><br>"
                    "4.3 - 4.4: Excellent (toll quality)<br>"
                    "4.0 - 4.2: Good (acceptable for most users)<br>"
                    "3.6 - 3.9: Fair (some users may be dissatisfied)<br>"
                    "3.1 - 3.5: Poor (many users dissatisfied)<br>"
                    "2.6 - 3.0: Bad (nearly all users dissatisfied)<br>"
                    "< 2.6: Unusable<br>"
                    "<br>"
                    "<b>Note:</b> Thresholds are inverted - lower MOS values trigger alerts. "
                    "Warning threshold should be higher than critical threshold."
                ),
                elements=[
                    Float(
                        title=_("Warning below"),
                        help=_("Alert when MOS drops below this value (e.g., 3.5)"),
                        default_value=3.5,
                        minvalue=0.0,
                        maxvalue=4.4,
                        validate=_validate_mos_value,
                    ),
                    Float(
                        title=_("Critical below"),
                        help=_("Critical alert when MOS drops below this value (e.g., 3.0)"),
                        default_value=3.0,
                        minvalue=0.0,
                        maxvalue=4.4,
                        validate=_validate_mos_value,
                    ),
                ],
            ),
        ),
    ]
    return Dictionary(
        title=_("Check hosts with PING (ICMP Echo Request)"),
        help=_(
            "This ruleset allows you to configure explicit PING monitoring of hosts. "
            "Usually a PING is being used as a host check, so this is not necessary. "
            "There are some situations, however, where this can be useful. One of them "
            "is when using the Checkmk Micro Core with SMART Ping and you want to "
            "track performance data of the PING to some hosts, nevertheless."
        ),
        elements=elements + check_icmp_params(),
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupActiveChecks,
        match_type="all",
        name=RuleGroup.ActiveChecks("icmp"),
        valuespec=_valuespec_active_checks_icmp,
    )
)