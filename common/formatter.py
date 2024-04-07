def toFormatNewLine(str):
    result = []

    if len(str) > 2000:
        sp = str.split("\n")
        newLine = ''
        for l in sp:
            if((newLine + l + '\n') <2000) :
                newLine = newLine + l + '\n'

            else:
                result.append(newLine)
                newLine = l + '\n'
            # end if
        # end for
        result.append(newLine)
    else:
        result.append(str)
    # end if


    return result

def toFormat(str):
    result = []

    if len(str) > 2000:
        sp = str.split()
        newLine = ''
        for l in sp:
            if((newLine + l + '\n') <2000) :
                newLine = newLine + l + '\n'

            else:
                result.append(newLine)
                newLine = l + '\n'
            # end if
        # end for
        result.append(newLine)
    else:
        result.append(str)
    # end if
    return result