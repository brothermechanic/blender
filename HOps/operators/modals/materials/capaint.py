import bpy

def carpaint_material(material = None, name= 'Carpaint'):
    if not material:
        material = bpy.data.materials.new (name)
    material.use_nodes = True
    material_nodes = material.node_tree.nodes
    material_nodes.clear()
    output = material_nodes.new(type="ShaderNodeOutputMaterial")
    
    paint = material_nodes.new('ShaderNodeGroup')
    paint.node_tree = carpaint_node_group()
    material.node_tree.links.new(paint.outputs[0], output.inputs[0]) 
    paint.location = [-300, output.location[1]]
    return (material, paint)

def carpaint_node_group():
    group_name = 'carpaint_shader'
    carpaint_shader = None
    try:
        carpaint_shader = bpy.data.node_groups[group_name]
        return carpaint_shader
    except:
        pass

    carpaint_shader = bpy.data.node_groups.new(group_name,'ShaderNodeTree')

    principled_carpaint = carpaint_shader.nodes.new("ShaderNodeBsdfPrincipled")
    principled_carpaint.location = [789, 105]
    principled_carpaint.name = "principled_carpaint"
    principled_carpaint.label = "principled_carpaint"
    #Node properties
    #node I/O
    principled_carpaint.inputs["Base Color"].default_value = [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]
    principled_carpaint.inputs["Subsurface"].default_value = 0.0
    principled_carpaint.inputs["Subsurface Radius"].default_value = [1.0, 0.20000000298023224, 0.10000000149011612]
    principled_carpaint.inputs["Subsurface Color"].default_value = [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]
    principled_carpaint.inputs["Metallic"].default_value = 0.0
    principled_carpaint.inputs["Specular"].default_value = 0.5
    principled_carpaint.inputs["Specular Tint"].default_value = 0.0
    principled_carpaint.inputs["Roughness"].default_value = 0.5
    principled_carpaint.inputs["Anisotropic"].default_value = 0.0
    principled_carpaint.inputs["Anisotropic Rotation"].default_value = 0.0
    principled_carpaint.inputs["Sheen"].default_value = 0.0
    principled_carpaint.inputs["Sheen Tint"].default_value = 0.5
    principled_carpaint.inputs["Clearcoat"].default_value = 1.0
    principled_carpaint.inputs["Clearcoat Roughness"].default_value = 0.029999999329447746
    principled_carpaint.inputs["IOR"].default_value = 1.4500000476837158
    principled_carpaint.inputs["Transmission"].default_value = 0.0
    principled_carpaint.inputs["Transmission Roughness"].default_value = 0.0
    principled_carpaint.inputs["Emission"].default_value = [0.0, 0.0, 0.0, 1.0]
    principled_carpaint.inputs["Alpha"].default_value = 1.0
    principled_carpaint.inputs["Normal"].default_value = [0.0, 0.0, 0.0]
    principled_carpaint.inputs["Clearcoat Normal"].default_value = [0.0, 0.0, 0.0]
    principled_carpaint.inputs["Tangent"].default_value = [0.0, 0.0, 0.0]

    carpaint_roughness_voronoi = carpaint_shader.nodes.new("ShaderNodeTexVoronoi")
    carpaint_roughness_voronoi.location = [-287, -494]
    carpaint_roughness_voronoi.name = "carpaint_roughness_voronoi"
    carpaint_roughness_voronoi.label = "carpaint_roughness_voronoi"
    #Node properties
    carpaint_roughness_voronoi.voronoi_dimensions = "4D"
    carpaint_roughness_voronoi.feature = "F1"
    carpaint_roughness_voronoi.distance = "EUCLIDEAN"
    #node I/O
    carpaint_roughness_voronoi.inputs["Vector"].default_value = [0.0, 0.0, 0.0]
    carpaint_roughness_voronoi.inputs["W"].default_value = 0.0
    carpaint_roughness_voronoi.inputs["Scale"].default_value = 4000.0
    carpaint_roughness_voronoi.inputs["Smoothness"].default_value = 1.0
    carpaint_roughness_voronoi.inputs["Exponent"].default_value = 0.5
    carpaint_roughness_voronoi.inputs["Randomness"].default_value = 1.0

    carpaint_colorramp = carpaint_shader.nodes.new("ShaderNodeValToRGB")
    carpaint_colorramp.location = [-65, -106]
    carpaint_colorramp.name = "carpaint_colorramp"
    carpaint_colorramp.label = "carpaint_colorramp"
    #Node properties
    carpaint_colorramp.color_ramp.color_mode = "RGB"
    carpaint_colorramp.color_ramp.interpolation = "LINEAR"
    carpaint_colorramp.color_ramp.elements[0].position = 0.0
    carpaint_colorramp.color_ramp.elements[0].color = [0.5534290075302124, 0.1514420062303543, 0.0514569990336895, 1.0]
    carpaint_colorramp.color_ramp.elements[1].position = 0.800000011920929
    carpaint_colorramp.color_ramp.elements[1].color = [1.0, 0.023302000015974045, 0.014751999638974667, 1.0]
    #node I/O
    carpaint_colorramp.inputs["Fac"].default_value = 0.5

    carpaint_hsv = carpaint_shader.nodes.new("ShaderNodeHueSaturation")
    carpaint_hsv.location = [540, 453]
    carpaint_hsv.name = "carpaint_hsv"
    carpaint_hsv.label = "carpaint_hsv"
    #Node properties
    #node I/O
    carpaint_hsv.inputs["Hue"].default_value = 0.8999999761581421
    carpaint_hsv.inputs["Saturation"].default_value = 1.0
    carpaint_hsv.inputs["Value"].default_value = 0.30000001192092896
    carpaint_hsv.inputs["Fac"].default_value = 1.0
    carpaint_hsv.inputs["Color"].default_value = [0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0]

    variation_saturation = carpaint_shader.nodes.new("ShaderNodeGroup")
    variation_saturation.location = [182, 561]
    variation_saturation.name = "variation_saturation"
    variation_saturation.label = "variation_saturation"
    #Node properties
    variation_saturation.node_tree = variation_group()
    #node I/O
    variation_saturation.inputs["Variation Amount"].default_value = 0.05000000074505806
    variation_saturation.inputs["Base Value"].default_value = 1.0
    variation_saturation.inputs["Object Info Random"].default_value = 0.5

    variation_value = carpaint_shader.nodes.new("ShaderNodeGroup")
    variation_value.location = [174, 368]
    variation_value.name = "variation_value"
    variation_value.label = "variation_value"
    #Node properties
    variation_value.node_tree = variation_group()
    #node I/O
    variation_value.inputs["Variation Amount"].default_value = 0.05000000074505806
    variation_value.inputs["Base Value"].default_value = 0.30000001192092896
    variation_value.inputs["Object Info Random"].default_value = 0.5

    Map_Range = carpaint_shader.nodes.new("ShaderNodeMapRange")
    Map_Range.location = [107, -490]
    Map_Range.name = "Map_Range"
    #Node properties
    #node I/O
    Map_Range.inputs["Value"].default_value = 1.0
    Map_Range.inputs["From Min"].default_value = 0.0
    Map_Range.inputs["From Max"].default_value = 1.0
    Map_Range.inputs["To Min"].default_value = 0.23999999463558197
    Map_Range.inputs["To Max"].default_value = 0.8799999952316284
    Map_Range.inputs["Steps"].default_value = 4.0

    carpaint_layerweight = carpaint_shader.nodes.new("ShaderNodeLayerWeight")
    carpaint_layerweight.location = [-237, -108]
    carpaint_layerweight.name = "carpaint_layerweight"
    carpaint_layerweight.label = "carpaint_layerweight"
    #Node properties
    #node I/O
    carpaint_layerweight.inputs["Blend"].default_value = 0.5
    carpaint_layerweight.inputs["Normal"].default_value = [0.0, 0.0, 0.0]

    tex_coord = carpaint_shader.nodes.new("ShaderNodeTexCoord")
    tex_coord.location = [-638, -548]
    tex_coord.name = "tex_coord"
    tex_coord.label = "tex_coord"
    #Node properties
    #node I/O

    variation_hue = carpaint_shader.nodes.new("ShaderNodeGroup")
    variation_hue.location = [173, 743]
    variation_hue.name = "variation_hue"
    variation_hue.label = "variation_hue"
    #Node properties
    variation_hue.node_tree = variation_group()
    #node I/O
    variation_hue.inputs["Variation Amount"].default_value = 0.05000000074505806
    variation_hue.inputs["Base Value"].default_value = 0.10000000149011612
    variation_hue.inputs["Object Info Random"].default_value = 0.5

    Group_Output = carpaint_shader.nodes.new("NodeGroupOutput")
    Group_Output.location = [1139, 100]
    Group_Output.name = "Group_Output"
    #Node properties

    Gorup_in = carpaint_shader.nodes.new("NodeGroupInput")
    Gorup_in.location = [-815, 467]
    Gorup_in.name = "Gorup_in"
    Gorup_in.label = "Gorup_in"
    #Node properties

    Object_Info = carpaint_shader.nodes.new("ShaderNodeObjectInfo")
    Object_Info.location = [-816, 657]
    Object_Info.name = "Object_Info"
    #Node properties
    #node I/O

    Reroute = carpaint_shader.nodes.new("NodeReroute")
    Reroute.location = [-368, 577]
    Reroute.name = "Reroute"
    #Node properties

    Math = carpaint_shader.nodes.new("ShaderNodeMath")
    Math.location = [-596, 656]
    Math.name = "Math"
    #Node properties
    Math.operation = "MULTIPLY"
    Math.use_clamp = False
    #node I/O
    Math.inputs[0].default_value = 0.5
    Math.inputs[1].default_value = 0.0
    Math.inputs[2].default_value = 0.0
    #group llinks
    carpaint_shader.links.new(carpaint_hsv.outputs["Color"], principled_carpaint.inputs["Base Color"])
    carpaint_shader.links.new(variation_hue.outputs["Color"], carpaint_hsv.inputs["Hue"])
    carpaint_shader.links.new(carpaint_colorramp.outputs["Color"], carpaint_hsv.inputs["Color"])
    carpaint_shader.links.new(carpaint_layerweight.outputs["Facing"], carpaint_colorramp.inputs["Fac"])
    carpaint_shader.links.new(tex_coord.outputs["Object"], carpaint_roughness_voronoi.inputs["Vector"])
    carpaint_shader.links.new(Reroute.outputs["Output"], variation_hue.inputs["Object Info Random"])
    carpaint_shader.links.new(variation_saturation.outputs["Color"], carpaint_hsv.inputs["Saturation"])
    carpaint_shader.links.new(Reroute.outputs["Output"], variation_saturation.inputs["Object Info Random"])
    carpaint_shader.links.new(Reroute.outputs["Output"], variation_value.inputs["Object Info Random"])
    carpaint_shader.links.new(variation_value.outputs["Color"], carpaint_hsv.inputs["Value"])
    carpaint_shader.links.new(Map_Range.outputs["Result"], principled_carpaint.inputs["Roughness"])
    carpaint_shader.links.new(carpaint_roughness_voronoi.outputs["Color"], Map_Range.inputs["Value"])
    carpaint_shader.links.new(Object_Info.outputs["Random"], Math.inputs[0])
    carpaint_shader.links.new(Math.outputs["Value"], Reroute.inputs[0])
    carpaint_shader.links.new(Gorup_in.outputs[0], variation_hue.inputs["Variation Amount"])
    carpaint_shader.links.new(Gorup_in.outputs[1], variation_hue.inputs["Base Value"])
    carpaint_shader.links.new(Gorup_in.outputs[2], variation_saturation.inputs["Variation Amount"])
    carpaint_shader.links.new(Gorup_in.outputs[3], variation_saturation.inputs["Base Value"])
    carpaint_shader.links.new(Gorup_in.outputs[4], variation_value.inputs["Variation Amount"])
    carpaint_shader.links.new(Gorup_in.outputs[5], variation_value.inputs["Base Value"])
    carpaint_shader.links.new(Gorup_in.outputs[6], principled_carpaint.inputs["Metallic"])
    carpaint_shader.links.new(Gorup_in.outputs[7], Map_Range.inputs["To Min"])
    carpaint_shader.links.new(Gorup_in.outputs[8], Map_Range.inputs["To Max"])
    carpaint_shader.links.new(Gorup_in.outputs[9], carpaint_roughness_voronoi.inputs["Scale"])
    carpaint_shader.links.new(Gorup_in.outputs[10], principled_carpaint.inputs["Clearcoat"])
    carpaint_shader.links.new(Gorup_in.outputs[11], principled_carpaint.inputs["Clearcoat Roughness"])
    carpaint_shader.links.new(Gorup_in.outputs[12], Math.inputs[1])
    carpaint_shader.links.new(principled_carpaint.outputs["BSDF"], Group_Output.inputs[0])
    Gorup_in.outputs[0].name = "Hue Variation"
    carpaint_shader.inputs[0].name = "Hue Variation"
    Gorup_in.outputs[1].name = "Hue Shift Base Value"
    carpaint_shader.inputs[1].name = "Hue Shift Base Value"
    Gorup_in.outputs[2].name = "Saturation Variation"
    carpaint_shader.inputs[2].name = "Saturation Variation"
    Gorup_in.outputs[3].name = "Saturation Base Value"
    carpaint_shader.inputs[3].name = "Saturation Base Value"
    Gorup_in.outputs[4].name = "Brightness Variation"
    carpaint_shader.inputs[4].name = "Brightness Variation"
    Gorup_in.outputs[5].name = "Brightness Value"
    carpaint_shader.inputs[5].name = "Brightness Value"
    Gorup_in.outputs[6].name = "Metallic"
    carpaint_shader.inputs[6].name = "Metallic"
    Gorup_in.outputs[7].name = "Flake Roughness Minimum"
    carpaint_shader.inputs[7].name = "Flake Roughness Minimum"
    Gorup_in.outputs[8].name = "Flake Roughness Maximum"
    carpaint_shader.inputs[8].name = "Flake Roughness Maximum"
    Gorup_in.outputs[9].name = "Flake Scale"
    carpaint_shader.inputs[9].name = "Flake Scale"
    Gorup_in.outputs[10].name = "Clearcoat"
    carpaint_shader.inputs[10].name = "Clearcoat"
    Gorup_in.outputs[11].name = "Clearcoat Roughness"
    carpaint_shader.inputs[11].name = "Clearcoat Roughness"
    Gorup_in.outputs[12].name = "Randomness"
    carpaint_shader.inputs[12].name = "Randomness"
    Group_Output.inputs[0].name = "BSDF"
    carpaint_shader.outputs[0].name = "BSDF"
    carpaint_shader.inputs["Hue Variation"].min_value = 0.0
    carpaint_shader.inputs["Hue Variation"].max_value = 1.0
    carpaint_shader.inputs["Hue Shift Base Value"].min_value = 0.0
    carpaint_shader.inputs["Hue Shift Base Value"].max_value = 1.0
    carpaint_shader.inputs["Saturation Variation"].min_value = 0.0
    carpaint_shader.inputs["Saturation Variation"].max_value = 1.0
    carpaint_shader.inputs["Saturation Base Value"].min_value = 0.0
    carpaint_shader.inputs["Saturation Base Value"].max_value = 1.0
    carpaint_shader.inputs["Brightness Variation"].min_value = 0.0
    carpaint_shader.inputs["Brightness Variation"].max_value = 1.0
    carpaint_shader.inputs["Brightness Value"].min_value = -1.0
    carpaint_shader.inputs["Brightness Value"].max_value = 1.0
    carpaint_shader.inputs["Metallic"].min_value = 0.0
    carpaint_shader.inputs["Metallic"].max_value = 1.0
    carpaint_shader.inputs["Flake Roughness Minimum"].min_value = 0.0
    carpaint_shader.inputs["Flake Roughness Minimum"].max_value = 1.0
    carpaint_shader.inputs["Flake Roughness Maximum"].min_value = 0.0
    carpaint_shader.inputs["Flake Roughness Maximum"].max_value = 1.0
    carpaint_shader.inputs["Flake Scale"].min_value = 1.0
    carpaint_shader.inputs["Flake Scale"].max_value = 20000.0
    carpaint_shader.inputs["Clearcoat"].min_value = 0.0
    carpaint_shader.inputs["Clearcoat"].max_value = 1.0
    carpaint_shader.inputs["Clearcoat Roughness"].min_value = 0.0
    carpaint_shader.inputs["Clearcoat Roughness"].max_value = 1.0
    carpaint_shader.inputs["Randomness"].min_value = 0.0
    carpaint_shader.inputs["Randomness"].max_value = 1.0

    return carpaint_shader


def variation_group():
    group_name = 'variation'
    variation = None
    try:
        variation = bpy.data.node_groups[group_name]
        return variation
    except:
        variation = bpy.data.node_groups.new(group_name,'ShaderNodeTree')

    Group_Output = variation.nodes.new("NodeGroupOutput")
    Group_Output.location = [580, -26]
    Group_Output.name = "Group_Output"
    #Node properties

    carpaint_shift_mix = variation.nodes.new("ShaderNodeMixRGB")
    carpaint_shift_mix.location = [249, 153]
    carpaint_shift_mix.name = "carpaint_shift_mix"
    carpaint_shift_mix.label = "carpaint_shift_mix"
    #Node properties
    carpaint_shift_mix.blend_type = "MIX"
    carpaint_shift_mix.use_clamp = True
    #node I/O
    carpaint_shift_mix.inputs["Fac"].default_value = 0.0
    carpaint_shift_mix.inputs["Color1"].default_value = [0.5, 0.5, 0.5, 1.0]
    carpaint_shift_mix.inputs["Color2"].default_value = [0.5, 0.5, 0.5, 1.0]

    Map_Range = variation.nodes.new("ShaderNodeMapRange")
    Map_Range.location = [-177, -30]
    Map_Range.name = "Map_Range"
    #Node properties
    #node I/O
    Map_Range.inputs["Value"].default_value = 1.0
    Map_Range.inputs["From Min"].default_value = 0.0
    Map_Range.inputs["From Max"].default_value = 1.0
    Map_Range.inputs["To Min"].default_value = 0.0
    Map_Range.inputs["To Max"].default_value = 1.0
    Map_Range.inputs["Steps"].default_value = 4.0

    Math = variation.nodes.new("ShaderNodeMath")
    Math.location = [-235, 301]
    Math.name = "Math"
    #Node properties
    Math.operation = "ADD"
    Math.use_clamp = False
    #node I/O
    Math.inputs[0].default_value = 0.5
    Math.inputs[1].default_value = 0.0
    Math.inputs[2].default_value = 0.0

    Group_Input = variation.nodes.new("NodeGroupInput")
    Group_Input.location = [-627, 142]
    Group_Input.name = "Group_Input"
    Group_Input.label = "variation"
    #Node properties
    #group llinks
    variation.links.new(Map_Range.outputs["Result"], carpaint_shift_mix.inputs["Color2"])
    variation.links.new(Math.outputs[0], carpaint_shift_mix.inputs["Color1"])
    variation.links.new(Group_Input.outputs[0], carpaint_shift_mix.inputs["Fac"])
    variation.links.new(Group_Input.outputs[1], Math.inputs["Value"])
    variation.links.new(Group_Input.outputs[2], Map_Range.inputs["Value"])
    variation.links.new(carpaint_shift_mix.outputs["Color"], Group_Output.inputs[0])
    Group_Input.outputs[0].name = "Variation Amount"
    variation.inputs[0].name = "Variation Amount"
    Group_Input.outputs[1].name = "Base Value"
    variation.inputs[1].name = "Base Value"
    Group_Input.outputs[2].name = "Object Info Random"
    variation.inputs[2].name = "Object Info Random"
    Group_Output.inputs[0].name = "Color"
    variation.outputs[0].name = "Color"

    return variation