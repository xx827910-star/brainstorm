"""
终端可视化工具
使用ASCII字符创建图表和可视化
"""
from typing import List, Dict, Tuple
import math


class TerminalVisualizer:
    """终端可视化器"""

    @staticmethod
    def create_line_chart(data: List[float],
                         width: int = 80,
                         height: int = 20,
                         title: str = "",
                         labels: List[str] = None) -> str:
        """
        创建ASCII线图

        Args:
            data: 数据点
            width: 图表宽度
            height: 图表高度
            title: 标题
            labels: X轴标签

        Returns:
            ASCII图表字符串
        """
        if not data:
            return "No data"

        # 标准化数据到图表高度
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1

        # 创建画布
        canvas = [[' ' for _ in range(width)] for _ in range(height)]

        # 绘制数据点
        for i, value in enumerate(data):
            if i >= width:
                break
            normalized = (value - min_val) / range_val
            y = int((1 - normalized) * (height - 1))
            y = max(0, min(height - 1, y))

            canvas[y][i] = '●'

            # 连接线
            if i > 0:
                prev_value = data[i - 1]
                prev_normalized = (prev_value - min_val) / range_val
                prev_y = int((1 - prev_normalized) * (height - 1))
                prev_y = max(0, min(height - 1, prev_y))

                # 绘制连接
                start_y, end_y = min(prev_y, y), max(prev_y, y)
                for yy in range(start_y, end_y + 1):
                    if canvas[yy][i] == ' ':
                        canvas[yy][i] = '│' if prev_y != y else '─'

        # 构建输出
        output = []
        if title:
            output.append(f"\n{'=' * width}")
            output.append(f"{title:^{width}}")
            output.append(f"{'=' * width}")

        # Y轴标签和图表
        for i, row in enumerate(canvas):
            value = max_val - (i / (height - 1)) * range_val
            label = f"{value:8.2f} │"
            output.append(label + ''.join(row))

        # X轴
        output.append(' ' * 10 + '└' + '─' * (width - 1))

        # X轴标签
        if labels:
            label_line = ' ' * 11
            step = max(1, len(labels) // 5)
            for i in range(0, len(labels), step):
                if i < width:
                    label_line += f"{labels[i]:<{step * 2}}"
            output.append(label_line[:width + 10])

        return '\n'.join(output)

    @staticmethod
    def create_bar_chart(data: Dict[str, float],
                        width: int = 50,
                        title: str = "") -> str:
        """
        创建ASCII柱状图

        Args:
            data: {label: value}
            width: 图表宽度
            title: 标题

        Returns:
            ASCII柱状图
        """
        if not data:
            return "No data"

        max_val = max(data.values())
        max_label_len = max(len(k) for k in data.keys())

        output = []
        if title:
            output.append(f"\n{title}")
            output.append('=' * (width + max_label_len + 5))

        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            bar_len = int((value / max_val) * width) if max_val > 0 else 0
            bar = '█' * bar_len
            output.append(f"{label:>{max_label_len}} │ {bar} {value:.2f}")

        return '\n'.join(output)

    @staticmethod
    def create_histogram(data: List[float],
                        bins: int = 10,
                        width: int = 50,
                        title: str = "") -> str:
        """
        创建ASCII直方图

        Args:
            data: 数据点
            bins: 分箱数量
            width: 图表宽度
            title: 标题

        Returns:
            ASCII直方图
        """
        if not data:
            return "No data"

        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val
        bin_width = range_val / bins if bins > 0 else 1

        # 分箱
        histogram = [0] * bins
        for value in data:
            if range_val == 0:
                bin_idx = 0
            else:
                bin_idx = int((value - min_val) / bin_width)
                bin_idx = min(bins - 1, bin_idx)
            histogram[bin_idx] += 1

        # 创建图表
        max_count = max(histogram)
        output = []

        if title:
            output.append(f"\n{title}")
            output.append('=' * (width + 20))

        for i, count in enumerate(histogram):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            bar_len = int((count / max_count) * width) if max_count > 0 else 0
            bar = '█' * bar_len

            output.append(f"[{bin_start:8.2f}-{bin_end:8.2f}] │ {bar} ({count})")

        return '\n'.join(output)

    @staticmethod
    def create_table(headers: List[str],
                    rows: List[List],
                    title: str = "") -> str:
        """
        创建ASCII表格

        Args:
            headers: 表头
            rows: 数据行
            title: 标题

        Returns:
            ASCII表格
        """
        if not headers or not rows:
            return "No data"

        # 计算列宽
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # 构建表格
        output = []

        if title:
            total_width = sum(col_widths) + len(headers) * 3 + 1
            output.append(f"\n{title}")
            output.append('=' * total_width)

        # 表头
        header_line = '│'
        for i, header in enumerate(headers):
            header_line += f" {header:<{col_widths[i]}} │"
        output.append(header_line)

        # 分隔线
        separator = '├'
        for width in col_widths:
            separator += '─' * (width + 2) + '┼'
        separator = separator[:-1] + '┤'
        output.append(separator)

        # 数据行
        for row in rows:
            row_line = '│'
            for i, cell in enumerate(row):
                # 格式化单元格
                if isinstance(cell, float):
                    cell_str = f"{cell:.4f}"
                else:
                    cell_str = str(cell)
                row_line += f" {cell_str:<{col_widths[i]}} │"
            output.append(row_line)

        # 底部
        bottom = '└'
        for width in col_widths:
            bottom += '─' * (width + 2) + '┴'
        bottom = bottom[:-1] + '┘'
        output.append(bottom)

        return '\n'.join(output)

    @staticmethod
    def create_gauge(value: float,
                    min_val: float,
                    max_val: float,
                    width: int = 50,
                    label: str = "",
                    zones: List[Tuple[float, str, str]] = None) -> str:
        """
        创建仪表盘

        Args:
            value: 当前值
            min_val: 最小值
            max_val: 最大值
            width: 宽度
            label: 标签
            zones: [(threshold, label, char), ...] 区域定义

        Returns:
            ASCII仪表盘
        """
        range_val = max_val - min_val
        position = int(((value - min_val) / range_val) * width) if range_val > 0 else 0
        position = max(0, min(width - 1, position))

        # 默认区域
        if zones is None:
            zones = [
                (0.33, "Low", '░'),
                (0.66, "Medium", '▒'),
                (1.0, "High", '▓')
            ]

        # 构建仪表
        gauge = []
        for i in range(width):
            ratio = i / width
            for threshold, _, char in zones:
                if ratio <= threshold:
                    gauge.append(char)
                    break

        gauge[position] = '▼'

        output = []
        if label:
            output.append(f"\n{label}")

        output.append(''.join(gauge))
        output.append(f"{min_val:<10}{value:^{width-20}.2f}{max_val:>{10}}")

        # 区域说明
        zone_labels = ' | '.join([f"{lbl}" for _, lbl, _ in zones])
        output.append(f"[{zone_labels}]")

        return '\n'.join(output)

    @staticmethod
    def create_sparkline(data: List[float], width: int = 40) -> str:
        """
        创建迷你线图（sparkline）

        Args:
            data: 数据点
            width: 宽度

        Returns:
            单行迷你图
        """
        if not data:
            return ""

        # 采样数据到指定宽度
        if len(data) > width:
            step = len(data) / width
            sampled = [data[int(i * step)] for i in range(width)]
        else:
            sampled = data

        # 使用Unicode字符创建迷你图
        min_val = min(sampled)
        max_val = max(sampled)
        range_val = max_val - min_val if max_val != min_val else 1

        chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        sparkline = ''

        for value in sampled:
            normalized = (value - min_val) / range_val
            char_idx = int(normalized * (len(chars) - 1))
            sparkline += chars[char_idx]

        return sparkline

    @staticmethod
    def format_large_number(num: float) -> str:
        """格式化大数字"""
        if abs(num) >= 1e12:
            return f"{num/1e12:.2f}T"
        elif abs(num) >= 1e9:
            return f"{num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"{num/1e6:.2f}M"
        elif abs(num) >= 1e3:
            return f"{num/1e3:.2f}K"
        else:
            return f"{num:.2f}"

    @staticmethod
    def create_multi_line_chart(data_series: Dict[str, List[float]],
                               width: int = 80,
                               height: int = 20,
                               title: str = "") -> str:
        """
        创建多条线的图表

        Args:
            data_series: {label: [values]}
            width: 宽度
            height: 高度
            title: 标题

        Returns:
            多线图
        """
        if not data_series:
            return "No data"

        # 找到全局最大最小值
        all_values = [v for values in data_series.values() for v in values]
        min_val = min(all_values)
        max_val = max(all_values)
        range_val = max_val - min_val if max_val != min_val else 1

        # 为每个系列分配字符
        chars = ['●', '○', '■', '□', '▲', '△', '◆', '◇']
        series_chars = {}
        for i, label in enumerate(data_series.keys()):
            series_chars[label] = chars[i % len(chars)]

        # 创建画布
        canvas = [[' ' for _ in range(width)] for _ in range(height)]

        # 绘制每个系列
        for label, data in data_series.items():
            char = series_chars[label]
            for i, value in enumerate(data):
                if i >= width:
                    break
                normalized = (value - min_val) / range_val
                y = int((1 - normalized) * (height - 1))
                y = max(0, min(height - 1, y))
                canvas[y][i] = char

        # 构建输出
        output = []
        if title:
            output.append(f"\n{'=' * width}")
            output.append(f"{title:^{width}}")
            output.append(f"{'=' * width}")

        # 图例
        legend = "Legend: " + " | ".join([f"{char} {label}"
                                        for label, char in series_chars.items()])
        output.append(legend)
        output.append('')

        # Y轴和图表
        for i, row in enumerate(canvas):
            value = max_val - (i / (height - 1)) * range_val
            output.append(f"{value:8.2f} │" + ''.join(row))

        # X轴
        output.append(' ' * 10 + '└' + '─' * (width - 1))

        return '\n'.join(output)
