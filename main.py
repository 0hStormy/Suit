import eel
import requests
import os

qemuCommand = '''
qemu-system-x86_64 \
-enable-kvm \
-M q35 \
-m 4096 -smp 2 -cpu host \
-drive file=$ISO \
-device virtio-tablet \
-device virtio-keyboard \
-device qemu-xhci,id=xhci \
-machine vmport=off \
-vga virtio \
-display sdl,gl=on \
-audiodev pa,id=snd0 -device AC97,audiodev=snd0 \
-net nic,model=virtio-net-pci -net user,hostfwd=tcp::4444-:5555 \
'''

def createPage():
    with open("os.list", "r") as f:
        choices = f.readlines()
    htmlOptions = ""
    for option in choices:
        optionButBetter = option.split(": ")
        htmlOptions = htmlOptions + f'''<option value="{optionButBetter[0]}">{optionButBetter[0]}</option>'''
    with open("ui/template.html", "r") as f:
        template = f.read()
    finishedHTML = template.replace("<!--Eel will fill this in-->", htmlOptions)
    with open("ui/actual.html", "w") as f:
        f.write(finishedHTML)

def downloadFile(url):
    print(url)
    fileName = os.path.basename(url).removesuffix("\n")
    r = requests.get(url, stream=True)

    print(fileName)

    if os.path.isfile(fileName) is True:
        print("Already downloaded, skipping...")
        return

    with open(fileName.removesuffix("\n"), "wb") as f:
        chunkSize = 8184
        totalChunks = 0
        for chunk in r.iter_content(chunk_size=chunkSize):
            if chunk:
                totalChunks = totalChunks + chunkSize
                print(f"{str(round((totalChunks / 1048576), 2)).removesuffix(".0")}mb downloaded...")
                try:
                    f.write(chunk)
                except IOError:
                    print("Chunk failed to write")
        print("Done!")

@eel.expose
def startVM(selectedOS, index):
    print(f"Selected OS: {selectedOS}")
    with open("os.yaml", "r") as f:
        choices = f.readlines()
    selected = choices[index]
    downloadFile(selected.split(": ")[1].removesuffix("\n"))
    actualCommand = qemuCommand.replace("$ISO", os.path.basename(selected.split(": ")[1]))
    os.system(actualCommand)

createPage()
eel.init('ui')
eel.start('actual.html')