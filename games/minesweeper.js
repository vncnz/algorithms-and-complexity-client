let bgMine = 'hsl(0, 80%, 50%)'
let bgFlag = 'hsl(0, 80%, 80%)'
let bgGray = "hsl(0, 0%, 80%)"
let bgGreen = "hsl(100, 80%, 80%)"

export const createDefinitionForMinesweeperGame = () => {
    let sz = 4
    let obj = {
        field: {
            xsize: sz,
            ysize: sz
        },
        info: {
            status: 'running',
            progression: 0,
            internalData: { mines: [3, 5] }
        },
        objects: []
    }

    for(let i = 0; i < sz; i++) {
        for(let j = 0; j < sz; j++) {
            let id = j*sz + i
            // let b = obj.info.internalData.mines.includes(id)
            obj.objects.push({
                id: j*sz + i,
                bgColor: bgGray,
                fgColor: 'black',
                rect: { x: i, y: j, w: 1, h: 1 },
                // text: b ? '⧳' : '⧲',
                text: `O`,
                events: [ 'click', 'contextmenu' ],
                internalData: null
            })
        }
    }
    obj.info.progression = obj.objects.filter(o => !!o.internalData).length / obj.objects.length
    return obj
}


export const simulateServerForMinesweeperGame = (objs, evtType, input) => {
    console.warn('Simulating server', objs, evtType, input)
    let output = JSON.parse(JSON.stringify(input)) // simulo una comunicazione col server quindi non modifico l'oggetto corrente, ovviamente!
    let objid = objs[0]
    let obj = output.objects.find(o => o.id === objid)

    let isMine = output.info.internalData.mines.includes(objid)
    let isLeftClick = evtType === 'contextmenu'
    if (isLeftClick) {
        obj.text = '🏴'
        obj.bgColor = bgFlag
    }
    else if (isMine) {
        obj.text = 'X'
        obj.bgColor = bgMine
        output.info.status = 'lose'
        output.objects.forEach(o => o.events = [])
    } else {
        obj.text = '🗸' // TODO: nearby mines number
        obj.bgColor = bgGreen
        obj.events = []
    }

    output.info.progression = output.objects.filter(o => o.events.length === 0).length / (output.objects.length - output.info.internalData.mines.length)
    if (output.info.progression === 1) {
        output.info.status = 'win'
        output.objects.forEach(o => o.events = [])
    }
    return output
}