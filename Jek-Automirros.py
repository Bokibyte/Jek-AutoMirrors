bl_info = {
	"name": "Jek Auto Mirrors",
	"author": "Bokibyte",
	"version": (1, 0, 0),
	"blender": (4, 0, 0),
	"location": "Properties > Modifiers",
	"description": "Add a Mirror modifier to newly created mesh objects",
	"category": "Object",
}

import bpy


_known_object_pointers = set()


def _remember_current_objects():
	_known_object_pointers.clear()
	_known_object_pointers.update(obj.as_pointer() for obj in bpy.data.objects)
	if _add_mirror_to_new_objects not in bpy.app.handlers.depsgraph_update_post:
		bpy.app.handlers.depsgraph_update_post.append(_add_mirror_to_new_objects)


@bpy.app.handlers.persistent
def _schedule_object_snapshot(_unused=None):
	if not bpy.app.timers.is_registered(_remember_current_objects):
		bpy.app.timers.register(_remember_current_objects, first_interval=0.0)


@bpy.app.handlers.persistent
def _add_mirror_to_new_objects(scene, _depsgraph):
	for obj in bpy.data.objects:
		pointer = obj.as_pointer()
		if pointer in _known_object_pointers:
			continue

		_known_object_pointers.add(pointer)
		if (
			scene is None
			or not scene.new_with_mirrors_enabled
			or obj.type != "MESH"
		):
			continue

		modifier = obj.modifiers.new(name="Mirror", type="MIRROR")
		modifier.mirror_object = scene.new_with_mirrors_anchor
		modifier.use_axis = scene.new_with_mirrors_axes


def _draw_new_mirrors_row(self, context):
	layout = self.layout
	scene = context.scene
	row = layout.row(align=True)
	row.prop(scene, "new_with_mirrors_enabled", text="New w/ Mirrors", toggle=True)
	settings = row.row(align=True)
	settings.enabled = scene.new_with_mirrors_enabled
	settings.popover(
		panel="OBJECT_PT_new_with_mirrors_settings",
		text="",
		icon="PREFERENCES",
	)


class OBJECT_PT_new_with_mirrors_settings(bpy.types.Panel):
	bl_label = "New w/ Mirrors"
	bl_idname = "OBJECT_PT_new_with_mirrors_settings"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "modifier"
	bl_options = {"INSTANCED"}

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		layout.prop(scene, "new_with_mirrors_anchor", text="Mirror Anchor")
		layout.label(text="Mirror Axes")
		layout.prop(scene, "new_with_mirrors_axes", text="")


def register():
	bpy.utils.register_class(OBJECT_PT_new_with_mirrors_settings)
	bpy.types.Scene.new_with_mirrors_enabled = bpy.props.BoolProperty(
		name="New w/ Mirrors",
		description="Add a Mirror modifier to each newly created mesh object",
		default=False,
	)
	bpy.types.Scene.new_with_mirrors_anchor = bpy.props.PointerProperty(
		name="Mirror Anchor",
		description="Object whose origin is used as the mirror reference",
		type=bpy.types.Object,
	)
	bpy.types.Scene.new_with_mirrors_axes = bpy.props.BoolVectorProperty(
		name="Mirror Axes",
		description="Axes enabled on Mirror modifiers added to new objects",
		size=3,
		subtype="XYZ",
		default=(True, False, False),
	)

	bpy.types.DATA_PT_modifiers.append(_draw_new_mirrors_row)
	bpy.app.handlers.load_post.append(_schedule_object_snapshot)
	_schedule_object_snapshot()


def unregister():
	bpy.types.DATA_PT_modifiers.remove(_draw_new_mirrors_row)
	if bpy.app.timers.is_registered(_remember_current_objects):
		bpy.app.timers.unregister(_remember_current_objects)
	if _add_mirror_to_new_objects in bpy.app.handlers.depsgraph_update_post:
		bpy.app.handlers.depsgraph_update_post.remove(_add_mirror_to_new_objects)
	if _schedule_object_snapshot in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(_schedule_object_snapshot)

	del bpy.types.Scene.new_with_mirrors_enabled
	del bpy.types.Scene.new_with_mirrors_anchor
	del bpy.types.Scene.new_with_mirrors_axes
	bpy.utils.unregister_class(OBJECT_PT_new_with_mirrors_settings)
	_known_object_pointers.clear()


if __name__ == "__main__":
	register()
