import html
import os
import tempfile

import pytest

from src.hexo_helper.app import FormulaModel

# --- Fixtures: 可复用的测试设置和资源 ---


@pytest.fixture
def empty_model():
    """提供一个全新的、空的 FormulaModel 实例。"""
    return FormulaModel()


@pytest.fixture(scope="function")
def model_with_temp_file():
    """
    创建一个 FormulaModel 和一个包含多种情况的临时 Markdown 文件。
    测试结束后会自动清理临时文件。
    """
    mock_md_content = """# 这是一个测试文档

这是一个有编号的公式：
$$
  E = mc^2 \\
  \\tag{1}
$$

这是一个没有编号的公式：
$$a^2 + b^2 = c^2$$

这是一个引用，应该被更新：<span class="formula-ref" data-formula-old="E = mc^2 \\"> ( 1 ) </span>。

这是另一个有编号的公式，它的编号是非数字：
  $$
    \\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}
    \\tag{alpha}
  $$

这是一个指向不存在公式的无效引用，应该被删除：<span class="formula-ref"> (99) </span>.

这是一个空公式块：
$$
  \\tag{will-be-4}
$$

"""
    temp_fd, temp_filepath = tempfile.mkstemp(suffix=".md", text=True)
    with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
        f.write(mock_md_content)

    model = FormulaModel()
    yield model, temp_filepath, mock_md_content
    os.remove(temp_filepath)


# --- Test Suite: 测试用例集 ---


class TestFormulaModelPytest:
    """使用 pytest 风格测试 FormulaModel 类。"""

    # --- 基础功能测试 ---

    def test_initialization(self, empty_model):
        """测试模型初始化状态是否正确。"""
        assert empty_model.filepath is None
        assert empty_model.file_content == ""
        assert empty_model.previous_file_content is None  # 新增：确认撤销状态为空
        assert empty_model.formulas == []
        assert empty_model.references == []
        assert not empty_model.is_dirty

    def test_load_file_and_parse_content(self, model_with_temp_file):
        """
        测试加载文件和解析内容的准确性。
        【已更新】: 增加了对 previous_file_content 的检查。
        """
        model, temp_filepath, mock_md_content = model_with_temp_file
        model.load_file(temp_filepath)

        assert model.filepath == temp_filepath
        assert model.file_content == mock_md_content
        assert not model.is_dirty
        assert model.previous_file_content is None  # 打开文件会重置撤销状态

        assert len(model.formulas) == 4
        assert model.formulas[0] == {"id": "1", "latex": "E = mc^2 \\"}
        assert model.formulas[1] == {"id": "无", "latex": "a^2 + b^2 = c^2"}
        assert model.formulas[2] == {"id": "alpha", "latex": "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}"}
        assert model.formulas[3] == {"id": "will-be-4", "latex": ""}  # 测试空公式

        assert len(model.references) == 2
        assert model.references[0]["ref_id"] == "1"
        assert model.references[1]["ref_id"] == "99"

    def test_get_processed_content_logic(self, model_with_temp_file):
        """测试核心的重新编号和引用更新逻辑。 (此测试逻辑未变，依然有效)"""
        model, temp_filepath, mock_md_content = model_with_temp_file
        model.load_file(temp_filepath)

        new_content, deleted_refs = model.get_processed_content()

        assert deleted_refs == 1  # (99) 这个引用被删除了

        # 1. 第一个公式应该被重新编号为 (1)
        assert (
            """$$
  E = mc^2 \\
  \\tag{1}
$$"""
            in new_content
        )

        # 2. 第二个公式（原来无编号）应该被编号为 (2)
        assert (
            """$$
  a^2 + b^2 = c^2
  \\tag{2}
$$"""
            in new_content
        )

        # 3. 第三个公式应该被重新编号为 (3)
        assert (
            """  $$
    \\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}
    \\tag{3}
  $$"""
            in new_content
        )

        # 4. 第四个空公式应该被编号为 (4)
        assert (
            """$$
  \\tag{4}
$$"""
            in new_content
        )

        # 5. 对公式 (1) 的引用应该被正确更新
        latex_for_ref1 = html.escape("E = mc^2 \\", quote=True)
        expected_ref1_span = f'<span class="formula-ref" data-formula="{latex_for_ref1}">({1})</span>'
        assert expected_ref1_span in new_content

        # 6. 无效引用 (99) 应该被删除
        assert "(99)" not in new_content

    def test_save_file_content(self, model_with_temp_file):
        """
        【已重写】测试保存文件功能。
        根据新逻辑，save_file_content 只写入文件，不改变模型状态。
        """
        model, temp_filepath, _ = model_with_temp_file
        new_content = "这是新的文件内容。"
        model.filepath = temp_filepath
        model.file_content = new_content
        model.is_dirty = True  # 手动设置状态，模拟控制器行为

        save_success = model.save_file_content()
        assert save_success

        # 验证核心改动：模型状态不应被 save_file_content 修改
        assert model.is_dirty is True

        # 验证文件内容确实已被写入
        with open(temp_filepath, encoding="utf-8") as f:
            read_content = f.read()
        assert read_content == new_content

    # --- 边缘情况测试 ---
    def test_process_empty_content(self, empty_model):
        """测试当内容为空时，处理函数是否能正常返回。"""
        result, count = empty_model.get_processed_content()
        assert result is None
        assert count == 0

    def test_process_content_with_no_formulas(self, empty_model):
        """测试没有公式的文档。"""
        empty_model.file_content = "这是一个没有公式的普通文档。"
        empty_model.parse_content()
        result, count = empty_model.get_processed_content()
        assert result is None
        assert count == 0

    # --- 【新增】撤销功能测试 ---

    def test_store_state_for_undo(self, empty_model):
        """测试存储撤销状态的功能。"""
        content = "Initial content."
        empty_model.file_content = content
        assert empty_model.previous_file_content is None

        empty_model.store_state_for_undo()
        assert empty_model.previous_file_content == content

    def test_undo_last_change_success(self, empty_model):
        """测试成功执行一次撤销操作。"""
        initial_content = "$$\\tag{1}$$"
        processed_content = "$$\\tag{1}$$"  # 在这个简单例子中，处理前后内容一致，但不影响测试逻辑

        # 1. 模拟处理前的状态
        empty_model.file_content = initial_content
        empty_model.parse_content()
        assert len(empty_model.formulas) == 1

        # 2. 模拟控制器保存状态并更新内容
        empty_model.store_state_for_undo()
        empty_model.file_content = processed_content
        empty_model.parse_content()

        # 3. 执行撤销
        undo_success = empty_model.undo_last_change()
        assert undo_success

        # 4. 验证撤销后的状态
        assert empty_model.file_content == initial_content
        assert empty_model.is_dirty is True  # 撤销后应为脏状态
        assert empty_model.previous_file_content is None  # 撤销是单步的
        # 确认内容被重新解析
        assert len(empty_model.formulas) == 1
        assert empty_model.formulas[0]["id"] == "1"

    def test_undo_last_change_without_history(self, empty_model):
        """测试在没有可撤销状态时调用撤销。"""
        original_content = "some content"
        empty_model.file_content = original_content
        empty_model.is_dirty = False

        undo_success = empty_model.undo_last_change()

        # 验证操作失败且模型状态未被改变
        assert not undo_success
        assert empty_model.file_content == original_content
        assert not empty_model.is_dirty
