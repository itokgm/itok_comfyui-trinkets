from comfy_api.latest import ComfyAPI,ComfyExtension, io
import re
import math


class itokrTrikets(ComfyExtension):
    # must be declared as async

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            recalc_resolution_adapter_ar
            # Add more nodes here
        ]

# can be declared async or not, both will work
async def comfy_entrypoint() -> itokrTrikets:
    return itokrTrikets()

def apply_rounding(val, b_size, method):
    match method:
        case "floor":
            return int((val // b_size) * b_size)
        case  "ceil":
            return int(math.ceil(val / b_size) * b_size)
        case __: # round
            return int(round(val / b_size) * b_size)

class recalc_resolution_adapter_ar(io.ComfyNode):
    rounding_meth = ("round", "floor", "ceil")
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="recalc_resolution_adapter_ar",
            display_name="RecalcResolutionAdapter",
            category="Utils",
            description="Recalculates the resolution based on the input aspect ratio. The output is rounded to a multiple of the grid_size.",
            inputs=[
                io.Int.Input("width"),
                io.Int.Input("height"),
                io.String.Input("aspect_ratio",  default="16:9", optional=True, tooltip="Enter the aspect ratio as a string. Accepts ratios like '4:3' or decimals like '1.333'."),
                io.Boolean.Input("calculate", default=True,
                            tooltip="select false, thru a calucurating"),
                io.Int.Input("grid_size", default=8, 
                             tooltip="Rounds the output to the nearest multiple of this value."),
                io.Combo.Input("rounding_method", cls.rounding_meth, default = "round",
                             tooltip="Method for rounding to the grid size"),
                ],
            outputs=[
                io.Int.Output("width"),
                io.Int.Output("height"),
            ]
        )

    @classmethod
    def execute(cls, width, height, grid_size, rounding_method, calculate,  aspect_ratio=None) -> io.NodeOutput:
        if ( not calculate) or (aspect_ratio == None) or ( aspect_ratio == ""):
            res_w = width
            res_h = height
        else:
            total_pix = width * height
            w_ar, h_ar = aspect_ratio.split(":")
            ar_str = re.sub(r"[^\d.:]", "",aspect_ratio)
            ar_w, ar_h = map(float, ar_str.split(":"))
            scale_ratio =   math.sqrt(total_pix / (ar_w * ar_h))
            res_w = apply_rounding(ar_w * scale_ratio, grid_size, rounding_method)
            res_h = apply_rounding(ar_h * scale_ratio, grid_size, rounding_method)
        return io.NodeOutput(res_w, res_h)