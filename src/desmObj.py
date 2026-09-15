# desmObj: obj file format to Desmos vertex lists.
# vertex colors will be interpolated for their faces
import sys
from pathlib import Path

# helper function to process face entries
def fp(s):
    return int(s.split("/")[0])
    
# avg two tuples of form (float, float, float)
def avg(a, b, c):
    return ((a[0]+b[0]+c[0])/3, (a[1]+b[1]+c[1])/3, (a[2]+b[2]+c[2])/3)

def name_parse(name):
    if len(name) < 2:
        return name
    else:
        return name[0]+"_{"+name[1:]+"}"

def sanitize(x):
    return "".join(c for c in x if c.isalnum())

def flatten(x):
    # flatten list of strings
    result = "["
    for s in x:
        result += s+","
    result = result[:-1] + "]"
    return result

def main(args):
    input_file = open(args[1])
    input_name = Path(input_file.name).stem

    output_name = input_name
    output_file = open(output_name + ".txt", "w")

    obj_name = sanitize(input_name)
    FLIP_AXES = (1,1,1)
    RENDER_HELPER = True

    # all colors given in (R, G, B) in the range [0, 1]
    vertices = [] # [ (float, float, float) ... ]
    faces = [] # [ (int, int, int) ... ]
    vertex_colors = [] # [ (float, float, float) ... ]
    face_colors = [] # [ (float, float, float) ... ]


    colors_enabled = False # default to false and change to true later if needed

    for line in input_file:
        entry = line.split()
        match entry[0]:
            case 'v':
                vertices.append((FLIP_AXES[0]*float(entry[1]),\
                                FLIP_AXES[1]*float(entry[2]),\
                                FLIP_AXES[2]*float(entry[3])))
                if len(entry) > 4:
                    colors_enabled = True
                if colors_enabled:
                    vertex_colors.append((float(entry[4]),\
                                        float(entry[5]),\
                                        float(entry[6])))
            case 'f':
                faces.append((fp(entry[1]),\
                            fp(entry[2]),\
                            fp(entry[3])))
            case _:
                pass

    if colors_enabled:
        # desmos does not support varied colors per polygon,
        # so vertex colors are averaged into a face color
        for face in faces:
            face_colors.append(avg(vertex_colors[face[0]-1],\
                            vertex_colors[face[1]-1],\
                            vertex_colors[face[2]-1]))
    

    result_dict = {"v" : name_parse(obj_name+"v")+"=",
                   "f" : name_parse(obj_name+"f")+"=",}

    result_dict["v"] += flatten("("+format(vertex[0], "f")+","\
                         + format(vertex[1], "f") + ","\
                         + format(vertex[2], "f") + ")" for vertex in vertices)

    result_dict["f"] += flatten("("+str(face[0]) + ","\
                         + str(face[1]) + ","\
                         + str(face[2]) + ")" for face in faces)

    if colors_enabled:
        # use rgb() of list instead of list of rgb() to save space
        result_dict["c"] = name_parse(obj_name+"c")+"=\\operatorname{rgb}("
        result_dict["c"] += flatten(str(int(255 * color[0])) for color in face_colors)+","
        result_dict["c"] += flatten(str(int(255 * color[1])) for color in face_colors)+","
        result_dict["c"] += flatten(str(int(255 * color[2])) for color in face_colors)
        result_dict["c"] += ")"
    
    result = ""
    for key in result_dict:
        result += result_dict[key] + "\n"

    if RENDER_HELPER:
        vname = name_parse(obj_name+"v")
        fname = name_parse(obj_name+"f")
        result += "\\operatorname{triangle}\\left("+\
                    vname+"\\left[x.x\\right],"+\
                    vname+"\\left[x.y\\right],"+\
                    vname+"\\left[x.z\\right]\\right)\\operatorname{for}x="+fname

    output_file.write(result)
    output_file.close()

if __name__ == "__main__":
    main(sys.argv)
