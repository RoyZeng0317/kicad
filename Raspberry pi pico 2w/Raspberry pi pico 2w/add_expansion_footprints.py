"""
KiCad Scripting Console Script
──────────────────────────────
Run this inside KiCad's Scripting Console (Tools > Scripting Console)
while the 'Raspberry pi pico 2w.kicad_pcb' file is open.

It adds footprints for:
  J4  - RJ45 with magnetics (HR911105A)
  J5  - USB-C Charging receptacle
  J6  - USB-C Data receptacle
  J7  - mini-HDMI Type D
  U3  - W5500 Ethernet controller (LQFP-80)
  Y2  - 25MHz Crystal (3225-4pin SMD)
  R20-R32, C20-C23  - Passives
"""
import pcbnew

board = pcbnew.GetBoard()

# ── Helpers ────────────────────────────────────────────────────────────────
def mm(x): return pcbnew.FromMM(x)

def add_footprint(lib, name, ref, val, x_mm, y_mm, rot_deg=0, side="F.Cu"):
    try:
        fp = pcbnew.FootprintLoad(lib, name)
    except Exception:
        print(f"  [WARN] Footprint not found: {lib}:{name}")
        fp = pcbnew.FOOTPRINT(board)
        fp.SetValue(val)

    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))
    fp.SetOrientationDegrees(rot_deg)
    if side == "B.Cu":
        fp.Flip(fp.GetPosition(), False)
    board.Add(fp)
    print(f"  Added {ref} ({name}) at ({x_mm}, {y_mm})")
    return fp

def set_net(fp, pad_num, net_name):
    net = board.FindNet(net_name)
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, net_name, 0)
        board.Add(net)
    for pad in fp.Pads():
        if pad.GetNumber() == str(pad_num):
            pad.SetNet(net)
            break

# ── Board origin (bottom-right area, extending existing layout) ────────────
# Existing board: roughly 100–165 mm X, 45–100 mm Y
# New connectors go on the right/bottom edges

print("Adding expansion footprints…")

# W5500 LQFP-80 – placed at right side, centre area
u3 = add_footprint("Package_QFP", "LQFP-80_12x12mm_P0.65mm",
                   "U3", "W5500", 185, 72)

# RJ45 – right edge, top area (panel-mount)
j4 = add_footprint("Connector_RJ", "RJ45_Amphenol_RJHSE538X_Horizontal",
                   "J4", "HR911105A", 185, 50, rot_deg=0)

# USB-C Charging – bottom edge left
j5 = add_footprint("Connector_USB", "USB_C_Receptacle_GCT_USB4085",
                   "J5", "USB-C Charging", 120, 102, rot_deg=90)

# USB-C Data – bottom edge centre
j6 = add_footprint("Connector_USB", "USB_C_Receptacle_GCT_USB4085",
                   "J6", "USB-C Data", 133, 102, rot_deg=90)

# mini-HDMI – bottom edge right
j7 = add_footprint("Connector_HDMI", "HDMI_D_mini_1.13mm",
                   "J7", "mini-HDMI", 148, 102, rot_deg=90)

# 25MHz Crystal for W5500
y2 = add_footprint("Crystal", "Crystal_SMD_3225-4Pin_3.2x2.5mm",
                   "Y2", "25MHz", 172, 82)

# W5500 decoupling capacitors (0402 100nF)
for i, (cx, cy) in enumerate([(178,65),(181,65),(184,65),(178,68)], start=20):
    add_footprint("Capacitor_SMD", "C_0402_1005Metric",
                  f"C{i}", "100n", cx, cy)

# CC resistors USB-C charging (5.1kΩ)
add_footprint("Resistor_SMD", "R_0402_1005Metric", "R20", "5.1k", 113, 97)
add_footprint("Resistor_SMD", "R_0402_1005Metric", "R21", "5.1k", 116, 97)

# CC resistors USB-C data (5.1kΩ)
add_footprint("Resistor_SMD", "R_0402_1005Metric", "R22", "5.1k", 126, 97)
add_footprint("Resistor_SMD", "R_0402_1005Metric", "R23", "5.1k", 129, 97)

# HDMI 50Ω series resistors (8 resistors for 4 diff pairs)
for i, cx in enumerate(range(140, 156, 2), start=24):
    add_footprint("Resistor_SMD", "R_0402_1005Metric", f"R{i}", "50R", cx, 97)

# RSET 100Ω for W5500
add_footprint("Resistor_SMD", "R_0402_1005Metric", "R32", "100R", 195, 82)

# ── Assign net names to key pads ──────────────────────────────────────────
print("\nAssigning nets…")

# W5500 SPI
for pad_n, net_n in [("14","W5500_CS"),("15","W5500_SCK"),
                     ("16","W5500_MOSI"),("17","W5500_MISO"),
                     ("18","W5500_RST"),("19","W5500_INT"),
                     ("3", "ETH_TX+"),("4","ETH_TX-"),
                     ("1","ETH_RX+"),("2","ETH_RX-")]:
    set_net(u3, pad_n, net_n)

# RJ45 magnetics
for pad_n, net_n in [("5","ETH_TX+"),("4","ETH_TX-"),
                     ("7","ETH_RX+"),("9","ETH_RX-")]:
    set_net(j4, pad_n, net_n)

# USB-C Data
for pad_n, net_n in [("B6","USBC_DP"),("B7","USBC_DM"),
                     ("A4","VBUS_DATA"),("A1","GND")]:
    set_net(j6, pad_n, net_n)

# USB-C Charging VBUS
for pad_n, net_n in [("A4","VBUS_IN"),("A1","GND")]:
    set_net(j5, pad_n, net_n)

# mini-HDMI
hdmi_map = [
    ("1","HDMI_D2P"),("3","HDMI_D2N"),
    ("4","HDMI_D1P"),("6","HDMI_D1N"),
    ("7","HDMI_D0P"),("9","HDMI_D0N"),
    ("10","HDMI_CLKP"),("12","HDMI_CLKN"),
    ("14","HDMI_DDC_SCL"),("15","HDMI_DDC_SDA"),
    ("16","HDMI_HPD"),
]
for pad_n, net_n in hdmi_map:
    set_net(j7, pad_n, net_n)

# ── Refresh and save ──────────────────────────────────────────────────────
pcbnew.Refresh()
board.Save(board.GetFileName())
print("\nDone – board saved. Run DRC to check for issues.")
print("Next steps:")
print("  1. Open KiCad PCB Editor and verify component placement")
print("  2. Run Tools > Update PCB from Schematic to pull in full netlist")
print("  3. Run DRC")
print("  4. Route inner GND plane (In1.Cu) and 3V3 plane (In2.Cu)")
print("  5. Route signal traces on F.Cu and B.Cu")
