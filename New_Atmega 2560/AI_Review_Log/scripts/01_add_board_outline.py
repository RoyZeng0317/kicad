import pcbnew
import sys

PATH = r"C:\Users\Roy\Documents\GitHub\kicad\New_Atmega 2560\New_Atmega 2560.kicad_pcb"
DRY_RUN = "--apply" not in sys.argv
MARGIN_MM = 3.0

board = pcbnew.LoadBoard(PATH)

INF = float('inf')
minx, miny, maxx, maxy = INF, INF, -INF, -INF

def upd(bbox):
    global minx, miny, maxx, maxy
    minx = min(minx, bbox.GetLeft())
    miny = min(miny, bbox.GetTop())
    maxx = max(maxx, bbox.GetRight())
    maxy = max(maxy, bbox.GetBottom())

n_fp = 0
for fp in board.GetFootprints():
    upd(fp.GetBoundingBox())
    n_fp += 1

n_tr = 0
for t in board.GetTracks():
    upd(t.GetBoundingBox())
    n_tr += 1

# check for any pre-existing Edge.Cuts drawings
existing_edges = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]

margin = pcbnew.FromMM(MARGIN_MM)
minx -= margin
miny -= margin
maxx += margin
maxy += margin

w_mm = pcbnew.ToMM(maxx - minx)
h_mm = pcbnew.ToMM(maxy - miny)

print(f"Footprints scanned: {n_fp}, Track/via items scanned: {n_tr}")
print(f"Existing Edge.Cuts drawing objects found: {len(existing_edges)}")
print(f"Computed board outline (with {MARGIN_MM}mm margin):")
print(f"  top-left     = ({pcbnew.ToMM(minx):.2f}, {pcbnew.ToMM(miny):.2f}) mm")
print(f"  bottom-right = ({pcbnew.ToMM(maxx):.2f}, {pcbnew.ToMM(maxy):.2f}) mm")
print(f"  size         = {w_mm:.2f} x {h_mm:.2f} mm")

if DRY_RUN:
    print("\n[DRY RUN] 沒有加入任何線段、沒有存檔。加上 --apply 才會實際寫入。")
    sys.exit(0)

if existing_edges:
    print("\n偵測到已存在 Edge.Cuts 物件，為避免重複／衝突，本次不自動加入，請人工確認。")
    sys.exit(1)

edge_layer = pcbnew.Edge_Cuts
line_width = pcbnew.FromMM(0.15)

def add_line(x1, y1, x2, y2):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(int(x1), int(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(int(x2), int(y2)))
    seg.SetLayer(edge_layer)
    seg.SetWidth(int(line_width))
    board.Add(seg)

add_line(minx, miny, maxx, miny)
add_line(maxx, miny, maxx, maxy)
add_line(maxx, maxy, minx, maxy)
add_line(minx, maxy, minx, miny)

pcbnew.SaveBoard(PATH, board)
print("\n已寫入 4 條 Edge.Cuts 線段並存檔。")
