from PySide6.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QHeaderView,
)
from PySide6.QtGui import QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class Main_Screen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        self.button = QPushButton("Generate tileset")
        self.button.clicked.connect(self.plot_voronoi)
        left_layout.addWidget(self.button)

        self.button2 = QPushButton("Generate icon")
        self.button2.clicked.connect(self.plot_voronoi_icon)
        left_layout.addWidget(self.button2)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect("button_press_event", self.on_plot_click)
        left_layout.addWidget(self.canvas)

        # right side is for displaying adjacency graph
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Coordinates", "Neighbors"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.highlight_point_from_table)
        self.table.setSelectionMode(QTableWidget.NoSelection)

        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        self.points = None
        self.vor = None
        self.highlighted_point = None
        self.neighbor_highlights = []
        self.neighbor_map = {}

        self.color_blank = QColor(255, 255, 255)
        self.color_selected = QColor(255, 255, 0)
        self.color_neighbors = QColor(255, 165, 0)

    def plot_voronoi(self):
        self.ax.clear()
        num_points = 10
        self.points = np.random.rand(num_points, 2) * 10

        # bounding box needed so edge is finite
        box_margin = 2
        bounding_box = np.array(
            [
                [-box_margin, -box_margin],
                [10 + box_margin, -box_margin],
                [10 + box_margin, 10 + box_margin],
                [-box_margin, 10 + box_margin],
            ]
        )
        all_points = np.vstack([self.points, bounding_box])

        self.vor = Voronoi(all_points)

        voronoi_plot_2d(self.vor, ax=self.ax, show_vertices=False, line_colors="b")

        # marks points
        self.ax.plot(self.points[:, 0], self.points[:, 1], "ro", markersize=5)

        # adds number next to points
        for i, point in enumerate(self.points):
            self.ax.text(
                point[0] + 0.2, point[1] + 0.2, str(i), color="black", fontsize=12
            )

        self.ax.set_xticks(np.arange(0, 11, 1))
        self.ax.set_yticks(np.arange(0, 11, 1))
        self.ax.grid(True, linestyle="--", linewidth=0.5)

        self.update_table()
        self.canvas.draw()

    def plot_voronoi_icon(self):
        self.ax.clear()

        # generate random points inside a 10x10 grid
        # [0, 0] to [0, 10]
        #        or
        # [0, 0] to [10, 0]
        num_points = 10
        points = np.random.rand(num_points, 2) * 10

        # adds a constraining bounding box corner points for easier sizing
        box_corners = np.array([[0, 0], [0, 10], [10, 0], [10, 10]])
        all_points = np.vstack([points, box_corners])

        vor = Voronoi(all_points)

        # drawing "borders", it's the connecting lines
        for simplex in vor.ridge_vertices:
            if -1 in simplex:
                # -1 is the infinite edges, so ignore it
                continue
            p1, p2 = vor.vertices[simplex]
            if all(0 <= p1) and all(p1 <= 10) and all(0 <= p2) and all(p2 <= 10):
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], "b-")

        self.ax.plot([0, 0, 10, 10, 0], [0, 10, 10, 0, 0], "k--", linewidth=1)

        self.ax.set_xticks(np.arange(0, 11, 1))
        self.ax.set_yticks(np.arange(0, 11, 1))
        self.ax.grid(True, linestyle="--", linewidth=0.5)

        self.canvas.draw()

    def update_table(self):
        self.table.setRowCount(len(self.points))
        self.table.setVerticalHeaderLabels([str(i) for i in range(len(self.points))])

        self.neighbor_map = {i: set() for i in range(len(self.points))}
        for p1, p2 in self.vor.ridge_points:
            # ignore bounding box points
            if p1 < len(self.points) and p2 < len(self.points):
                self.neighbor_map[p1].add(p2)
                self.neighbor_map[p2].add(p1)

        for i, point in enumerate(self.points):
            coord_text = f"({point[0]:.2f}, {point[1]:.2f})"
            coord_text_widget = QTableWidgetItem(coord_text)
            coord_text_widget.setFlags(coord_text_widget.flags() & ~Qt.ItemIsEditable)

            neighbor_text = ", ".join(str(n) for n in self.neighbor_map[i])
            neighbor_text_widget = QTableWidgetItem(neighbor_text)
            neighbor_text_widget.setFlags(
                neighbor_text_widget.flags() & ~Qt.ItemIsEditable
            )

            self.table.setItem(i, 0, coord_text_widget)
            self.table.setItem(i, 1, neighbor_text_widget)

    def highlight_point_from_table(self, row, _):
        self.highlight_point(row)

    def highlight_point(self, selected_idx):
        if self.highlighted_point:
            self.highlighted_point.remove()
        for highlight in self.neighbor_highlights:
            highlight.remove()
        self.neighbor_highlights.clear()

        selected_point = self.points[selected_idx]
        self.highlighted_point = self.ax.plot(
            selected_point[0],
            selected_point[1],
            "yo",
            markersize=8,
            markeredgecolor="black",
        )[0]

        for neighbor_idx in self.neighbor_map[selected_idx]:
            neighbor_point = self.points[neighbor_idx]
            highlight = self.ax.plot(
                neighbor_point[0],
                neighbor_point[1],
                "orange",
                markersize=8,
                markeredgecolor="black",
            )[0]
            self.neighbor_highlights.append(highlight)

        self.reset_table_colors()

        self.set_row_color(
            selected_idx,
            self.color_selected,
        )

        for neighbor_idx in self.neighbor_map[selected_idx]:
            self.set_row_color(
                neighbor_idx,
                self.color_neighbors,
            )

        self.canvas.draw()

    # allows clicking inside area of the border and goes to nearest point
    # colors the selected point as well as highlight the related table info
    def on_plot_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        distances = np.linalg.norm(
            self.points - np.array([event.xdata, event.ydata]), axis=1
        )
        closest_idx = np.argmin(distances)

        # self.table.selectRow(closest_idx)
        self.highlight_point(closest_idx)

    def reset_table_colors(self):
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.item(row, col).setBackground(
                    self.color_blank,
                )

    def set_row_color(self, row, color):
        for col in range(self.table.columnCount()):
            self.table.item(row, col).setBackground(color)
