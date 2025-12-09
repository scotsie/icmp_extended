# CheckMK ICMP Active Check Extension (Jitter & MOS Monitoring)

![CheckMK](https://img.shields.io/badge/CheckMK-2.3-blue)
![Python](https://img.shields.io/badge/Python-3-green)
![License](https://img.shields.io/badge/License-GPLv2-red)

## Description

This CheckMK extension enhances the built-in ICMP (ping) active check with advanced network quality metrics essential for VoIP and real-time application monitoring. It adds support for:

- **Jitter Monitoring** - Measures variation in packet arrival times (network stability)
- **MOS (Mean Opinion Score)** - Provides a single quality score for voice call quality (1.0-4.4 scale)

The plugin maintains full backward compatibility with the standard ICMP check while adding these new capabilities through optional configuration parameters.

## Features

- ✅ **Jitter Thresholds** - Configure warning/critical thresholds for network jitter in milliseconds
- ✅ **MOS Score Monitoring** - Track voice quality with industry-standard MOS scoring
- ✅ **Enhanced Graphing** - Dedicated graphs for jitter metrics and MOS scores
- ✅ **Performance Data** - Comprehensive perfdata collection for trending and analysis
- ✅ **Backward Compatible** - Works alongside existing ICMP checks without modifications
- ✅ **VoIP Optimized** - Ideal for monitoring SIP trunks, VoIP gateways, and real-time services

## Use Cases

- **VoIP Infrastructure** - Monitor SIP trunks, PBX systems, and VoIP gateways
- **Real-time Applications** - Gaming servers, video conferencing, live streaming
- **Network Quality Assessment** - Identify unstable links affecting user experience
- **SLA Compliance** - Track network quality metrics against service level agreements
- **Troubleshooting** - Diagnose network issues affecting voice/video quality

## Requirements

- CheckMK 2.3.0 or later
- Check_ICMP plugin with jitter support (included in CheckMK 2.3+)
- Python 3

## Installation

### Manual Installation

1. Create the plugin directory structure:
```bash
mkdir -p ~/local/lib/python3/cmk_addons/plugins/icmp_extended/{server_side_calls,rulesets,graphing}
```

2. Copy the plugin files to their respective locations:
```bash
# Server-side calls (command builder)
cp server_side_calls/icmp.py ~/local/lib/python3/cmk_addons/plugins/icmp_extended/server_side_calls/

# Rulesets (WebUI configuration)
cp rulesets/icmp.py ~/local/lib/python3/cmk_addons/plugins/icmp_extended/rulesets/

# Graphing (metrics and graphs)
cp graphing/icmp.py ~/local/lib/python3/cmk_addons/plugins/icmp_extended/graphing/
```

3. Set proper ownership:
```bash
SITE_NAME=$(omd config show SITE)
chown -R $SITE_NAME:$SITE_NAME ~/local/lib/python3/cmk_addons/
```

4. Restart the CheckMK site:
```bash
omd restart
```

5. Activate changes in the WebUI:
   - Navigate to **Setup → Activate Changes**
   - Click **Activate on selected sites**

### Package Installation (if available)
```bash
mkp install icmp_extended-1.0.mkp
```

## Configuration

### Creating a Rule

1. Navigate to **Setup → Host monitoring → HTTP, TCP, Email, ... → Check hosts with PING (ICMP Echo Request)**
2. Create a new rule or edit an existing one
3. Configure the new options:

#### Jitter Configuration

**Field:** Jitter thresholds

- **Warning threshold** (ms): Alert when jitter exceeds this value (default: 40ms)
- **Critical threshold** (ms): Critical alert when jitter exceeds this value (default: 80ms)

**Recommended values:**
- VoIP/Video: Warning 30ms, Critical 50ms
- General monitoring: Warning 40ms, Critical 80ms
- Gaming/Real-time: Warning 20ms, Critical 40ms

#### MOS Configuration

**Field:** Mean Opinion Score (MOS) thresholds

- **Warning threshold**: Alert when MOS drops below this value (default: 3.5)
- **Critical threshold**: Critical alert when MOS drops below this value (default: 3.0)

**MOS Score Guide:**
- 4.3 - 4.4: Excellent (toll quality)
- 4.0 - 4.2: Good (acceptable for most users)
- 3.6 - 3.9: Fair (some users may be dissatisfied)
- 3.1 - 3.5: Poor (many users dissatisfied)
- 2.6 - 3.0: Bad (nearly all users dissatisfied)
- < 2.6: Unusable

**Note:** MOS thresholds are inverted - warning should be higher than critical (e.g., warn at 3.5, critical at 3.0)

**Recommended values:**
- VoIP/Business calls: Warning 3.8, Critical 3.5
- General monitoring: Warning 3.5, Critical 3.0
- Basic monitoring: Warning 3.0, Critical 2.6

### Example Configurations

#### VoIP Gateway Monitoring
```
Description: VoIP Gateway Quality
Jitter: 30ms / 50ms (warn/crit)
MOS: 3.8 / 3.5 (warn/crit)
Packets: 10
```

#### General Network Quality
```
Description: Network Quality Check
Jitter: 40ms / 80ms (warn/crit)
MOS: 3.5 / 3.0 (warn/crit)
Packets: 5
```

## Generated Check Commands

The plugin generates check_icmp commands with the appropriate flags:

**Standard check (backward compatible):**
```bash
check_icmp -R 200.00ms,500.00ms -P 80%,100% 192.168.1.1
```

**With jitter monitoring:**
```bash
check_icmp -R 200.00ms,500.00ms -P 80%,100% -J 40.00ms,80.00ms 192.168.1.1
```

**With MOS monitoring:**
```bash
check_icmp -R 200.00ms,500.00ms -P 80%,100% -M 3.5,3.0 192.168.1.1
```

**With both jitter and MOS:**
```bash
check_icmp -R 200.00ms,500.00ms -P 80%,100% -J 40.00ms,80.00ms -M 3.5,3.0 192.168.1.1
```

## Performance Data

The plugin collects the following metrics:

| Metric | Description | Unit |
|--------|-------------|------|
| `rta` | Round trip average | seconds |
| `pl` | Packet loss | percent |
| `rtmax` | Maximum round trip time | seconds |
| `rtmin` | Minimum round trip time | seconds |
| `jitter_avg` | Average jitter | seconds |
| `jitter_max` | Maximum jitter | seconds |
| `jitter_min` | Minimum jitter | seconds |
| `mos` | Mean Opinion Score | score (0-4.4) |

## Graphing

The extension provides the following graphs:

1. **Network Jitter** - Line graph showing average, maximum, and minimum jitter over time
2. **Voice Quality (MOS)** - Line graph displaying MOS score trends
3. **Perfometers** - Visual indicators in service list showing current jitter and MOS values

## Troubleshooting

### Plugin not appearing in WebUI
```bash
# Clear Python cache
rm -rf ~/var/check_mk/web/*/__pycache__
omd restart apache
```

### Check not generating metrics
```bash
# Test the check manually
/omd/sites/<sitename>/lib/nagios/plugins/check_icmp -H <target> -R 200ms,500ms -P 80%,100% -J 40ms,80ms -M 3.5,3.0 -n 5

# Verify command generation
cmk -D <hostname> | grep check_icmp

# Check service discovery
cmk -vII <hostname>
```

### Graphs not displaying
```bash
# Verify metrics are being collected
ls -la ~/var/check_mk/rrd/<hostname>/PING*

# Check for graphing errors
tail -f ~/var/log/web.log

# Restart to reload graphing definitions
omd restart
```

### Unit mismatch errors

Ensure all time-based metrics use consistent units (`DecimalNotation("s")`). Check the graphing configuration file.

## Development

### Directory Structure
```
icmp_extended/
├── server_side_calls/
│   └── icmp.py          # Command builder and parameter parsing
├── rulesets/
│   └── icmp.py          # WebUI form configuration
├── graphing/
│   └── icmp.py          # Metrics and graph definitions
└── README.md
```

### Testing
```bash
# Test Python syntax
python3 -m py_compile ~/local/lib/python3/cmk_addons/plugins/icmp_extended/server_side_calls/icmp.py
python3 -m py_compile ~/local/lib/python3/cmk_addons/plugins/icmp_extended/rulesets/icmp.py
python3 -m py_compile ~/local/lib/python3/cmk_addons/plugins/icmp_extended/graphing/icmp.py

# Test check execution
cmk --debug -vII <test_hostname>

# Verify command generation
cmk -D <test_hostname> | grep -A5 check_icmp
```

### Adding New Metrics

To add additional check_icmp options (e.g., `-S` for score mode):

1. Update `ICMPParams` model in `server_side_calls/icmp.py`
2. Add form field in `rulesets/icmp.py`
3. Modify `get_common_arguments()` to include the new flag
4. Create metric and graph definitions in `graphing/icmp.py`

## Technical Details

### CheckMK 2.3 Plugin Architecture

This plugin uses CheckMK 2.3's modern plugin structure:

- **Server-side calls API** (`cmk.server_side_calls.v1`) - For command generation
- **Pydantic models** - For parameter validation
- **Graphing API v1** (`cmk.graphing.v1`) - For metrics and graphs
- **Local plugin directory** (`cmk_addons/plugins/`) - For custom extensions

### Command Building Logic

The plugin uses explicit flag specification (`-R`, `-P`, `-J`, `-M`) instead of the legacy `-w`/`-c` format. This provides better control and clarity when combining multiple metrics.

### Backward Compatibility

- Existing ICMP checks continue to work without modification
- Jitter and MOS parameters are optional
- When not configured, the check behaves identically to the standard ICMP check

## Known Limitations

- MOS calculation depends on check_icmp plugin version with MOS support
- Jitter requires minimum 3-5 packets for accurate measurement
- IPv6 support inherits limitations from underlying check_icmp plugin

## Contributing

Contributions are welcome! Areas for enhancement:

- Additional check_icmp options (Score mode `-S`, Out of order detection `-O`)
- Combined quality dashboard/graph
- Threshold templates for common use cases
- Additional metric correlations

## Support

For issues, questions, or feature requests:

1. Check the troubleshooting section above
2. Review CheckMK logs: `~/var/log/web.log` and `~/var/log/cmc.log`
3. Test check_icmp directly to isolate plugin vs. check issues
4. Verify CheckMK version compatibility (2.3.0+)

## License

This extension follows CheckMK's licensing:
- Copyright (C) 2019 Checkmk GmbH
- License: GNU General Public License v2
- Part of Checkmk (https://checkmk.com)

## Credits

- Based on CheckMK's built-in ICMP active check
- Developed for enhanced VoIP and real-time application monitoring
- Inspired by operational needs in telecommunications infrastructure

## Changelog

### Version 1.0.0 (Initial Release)
- Added jitter monitoring with configurable thresholds
- Added MOS (Mean Opinion Score) monitoring
- Enhanced graphing with dedicated jitter and MOS graphs
- Full backward compatibility with standard ICMP checks
- Support for CheckMK 2.3 plugin architecture