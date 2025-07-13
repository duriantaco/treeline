from treeline import TreeRenderer

renderer = TreeRenderer(
    show_code_structure=True,
    max_depth=2,
    show_size=True,
    show_file_count=True
)
renderer.render("../treeline")