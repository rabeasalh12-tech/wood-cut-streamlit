streamlit_app/
├── app.py                     # واجهة Streamlit
├── config.py                  # الثوابت (Kerf, Trim, Board Size)
├── models.py                  # تعريف البيانات (Piece, Board)
├── optimizer.py               # محرك 2D Bin Packing
├── calculator.py              # خصم الشريط، التطهير، السلاح
├── layout_drawer.py           # رسم الكروكي
├── pdf_exporter.py             # إخراج PDF
└── utils.py
with st.sidebar:
    st.header("⚙️ الإعدادات العامة")

    kerf = st.number_input("سمك سلاح المنشار (mm)", 0.0, 10.0, 3.2)
    trim = st.number_input("التطهير من كل جانب (mm)", 0.0, 50.0, 10.0)

    board_length = st.number_input("طول اللوح الخام (mm)", 1000, 6000, 2800)
    board_width  = st.number_input("عرض اللوح الخام (mm)", 500, 2500, 2070)
    board_thick  = st.number_input("سماكة اللوح (mm)", 6, 40, 18)
    with st.sidebar:
usable_length = board_length - 2 * trim
usable_width  = board_width  - 2 * trim
@dataclass
class Piece:
    name: str
    final_length: float
    final_width: float
    quantity: int
    grain: str  # "L" أو "W"
    edge_left: float
    edge_right: float
    edge_top: float
    edge_bottom: float
    def calculate_cut_size(piece: Piece):
    cut_length = piece.final_length - (piece.edge_left + piece.edge_right)
    cut_width  = piece.final_width  - (piece.edge_top  + piece.edge_bottom)

    if cut_length <= 0 or cut_width <= 0:
 raise ValueError(f"❌ خطأ في شريط الحافة للقطعة {piece.name}")

    return cut_length, cut_width
    def allowed_rotations(piece):
    if piece.grain == "L":
        return [(piece.cut_length, piece.cut_width)]
    else:
        return [
            (piece.cut_length, piece.cut_width),
            (piece.cut_width, piece.cut_length)
        ]
        def place_piece(board, piece):
    for free_rect in board.free_rectangles:
        if fits_with_kerf(free_rect, piece):
            place()
            split_free_space_with_kerf()
            return True
    return False
    def draw_board_layout(board):
    fig, ax = plt.subplots()

    ax.set_xlim(0, board.width)
    ax.set_ylim(0, board.length)

    for piece in board.placed_pieces:
        rect = patches.Rectangle(
            (piece.x, piece.y),
            piece.width,
            piece.length,
            fill=False
        )
        ax.add_patch(rect)
        ax.text(...)
        cut_size = final_size - edge_banding
        waste_area = board_area - sum(piece_areas)
waste_percent = waste_area / board_area * 100
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
