export const createDefinitionForFlipGame = () => {
    let sz = 4
    let obj = {
        field: {
            xsize: sz,
            ysize: sz
        },
        info: {
            status: 'running',
            progression: 0
        },
        objects: []
    }
    let lightUp = 'hsl(0, 0%, 80%)'
    let lightDown = "hsl(0, 0%, 20%)"
    for(let i = 0; i < sz; i++) {
        for(let j = 0; j < sz; j++) {
            let b = Math.random() > .5
            obj.objects.push({
                id: j*sz + i,
                bgColor: b ? lightUp : lightDown,
                fgColor: b ? 'black' : 'white',
                rect: { x: i, y: j, w: 1, h: 1 },
                // text: b ? '⧳' : '⧲',
                text: `${j*sz + i}`, // '¤',
                events: [ 'click' ],
                internalData: b
            })
        }
    }
    obj.info.progression = obj.objects.filter(o => !!o.internalData).length / obj.objects.length
    return obj
}


export const simulateServerForFlipGame = (objs, evtType, input) => {
    console.warn('Simulating server', objs, evtType, input)
    let output = JSON.parse(JSON.stringify(input)) // simulo una comunicazione col server quindi non modifico l'oggetto corrente, ovviamente!
    let obj = objs[0]
    let lightUp = 'hsl(0, 0%, 80%)'
    let lightDown = "hsl(0, 0%, 20%)"
    output.objects.forEach(o => {
        let row = output.field.xsize
        let xdiff = (o.id % row) - (obj % row)
        let ydiff = Math.ceil((o.id + 1) / row) - Math.ceil((obj + 1) / row)

        if ((xdiff == 0 && Math.abs(ydiff) < 2) ||
            (ydiff == 0 && Math.abs(xdiff) < 2)) {
                console.log(`${o.id} has xdiff ${xdiff} and ydiff ${ydiff} from ${obj}`)
            let b = !o.internalData
            o.bgColor = b ? lightUp : lightDown
            o.fgColor = b ? 'black' : 'white'
            // o.text = b ? '⧳' : '⧲'
            o.internalData = b
        }
    })
    output.info.progression = output.objects.filter(o => !!o.internalData).length / output.objects.length
    output.info.status = output.info.progression === 1 ? 'win' : 'running'
    return output
}