# desmObj: obj file format to Desmos vertex lists.
# vertex colors will be interpolated for their faces
import sys

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

def main(args):
    OBJECT_NAME = "object"
    OUTPUT_NAME = "output"
    FLIP_AXES = (-1,1,1)
    # subscripts used: v f c

    
    
    obj_file = open(args[1])
    output_file = open(OUTPUT_NAME + ".txt", "w")
    # all colors given in (R, G, B) in the range [0, 1]
    vertices = [] # [ (float, float, float) ... ]
    vertex_colors = [] # [ (float, float, float) ... ]
    face_colors = [] # [ (float, float, float) ... ]
    faces = [] # [ (int, int, int) ... ]
    for line in obj_file:
        entry = line.split()
        match entry[0]:
            case 'v':
                vertices.append((FLIP_AXES[0]*float(entry[1]),\
                                FLIP_AXES[1]*float(entry[2]),\
                                FLIP_AXES[2]*float(entry[3])))
                vertex_colors.append((float(entry[4]),\
                                    float(entry[5]),\
                                    float(entry[6])))
            case 'f':
                faces.append((fp(entry[1]),\
                            fp(entry[2]),\
                            fp(entry[3])))
            case _:
                pass

    # desmos does not support varied colors per polygon,
    # so vertex colors are averaged into a face color
    for face in faces:
        face_color = avg(vertex_colors[face[0]-1],\
                          vertex_colors[face[1]-1],\
                              vertex_colors[face[2]-1])
        face_colors.append(face_color)
    

    result_dict = {"v" : name_parse(OBJECT_NAME+"v")+"=\\left[",
                   "f" : name_parse(OBJECT_NAME+"f")+"=\\left[",
                   "c" : name_parse(OBJECT_NAME+"c")+"=\\left["}
    
    for vertex in vertices:
        # format() used to avoid str() making, for exmaple, 1e-06
        # which would mess up the stringifying
        result_dict["v"] += "\\left("+format(vertex[0], "f")+","\
                         + format(vertex[1], "f") + ","\
                         + format(vertex[2], "f") + "\\right),"

    # remove the last comma from the string and add ending bracket
    result_dict["v"] = result_dict["v"][:-1] + "\\right]"

    for face in faces:
        result_dict["f"] += "\\left("+str(face[0]) + ","\
                         + str(face[1]) + ","\
                         + str(face[2]) + "\\right),"

    result_dict["f"] = result_dict["f"][:-1] + "\\right]"
    
    for color in face_colors:
        result_dict["c"] += "\\operatorname{rgb}\\left("\
                            + str(int(255 * color[0])) + ","\
                            + str(int(255 * color[1])) + ","\
                            + str(int(255 * color[2])) + "\\right),"
    result_dict["c"] = result_dict["c"][:-1] + "\\right]"
    
    result = ""
    for key in result_dict:
        result += result_dict[key] + "\n"

    output_file.write(result)
    output_file.close()

if __name__ == "__main__":
    main(sys.argv)
