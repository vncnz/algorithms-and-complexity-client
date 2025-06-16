export const createDefinitionForFlipGame = () => {
    let sz = 4
    let game = {
        field: {
            xsize: sz,
            ysize: sz
        },
        playStatus: {
            status: 'running',
            progression: 0
        },
        objects: {},
        events: {}
    }
    let lightUp = 'hsl(0, 0%, 80%)'
    let lightDown = "hsl(0, 0%, 20%)"
    for(let i = 0; i < sz; i++) {
        for(let j = 0; j < sz; j++) {
            let b = Math.random() > .5
            let id = j*sz + i
            game.objects[id] = {
                id,
                bgColor: b ? lightUp : lightDown,
                fgColor: b ? 'black' : 'white',
                rect: { x: i, y: j, w: 1, h: 1 },
                // text: b ? '⧳' : '⧲',
                text: `${j*sz + i}`, // '¤',
                internalData: b
            }
            game.events[id] = [ 'click' ]
        }
    }
    game.playStatus.progression = Object.values(game.objects).filter(o => !!o.internalData).length / Object.values(game.objects).length
    return game
}


export const simulateServerForFlipGame = (objs, evtType, input) => {
    console.warn('Simulating server', objs, evtType, input)
    let output = JSON.parse(JSON.stringify(input)) // simulo una comunicazione col server quindi non modifico l'oggetto corrente, ovviamente!
    let obj = objs[0]
    let lightUp = 'hsl(0, 0%, 80%)'
    let lightDown = "hsl(0, 0%, 20%)"
    Object.values(output.objects).forEach(o => {
        let row = output.field.xsize
        let xdiff = (o.id % row) - (obj % row)
        let ydiff = Math.ceil((o.id + 1) / row) - Math.ceil((obj + 1) / row)

        if ((xdiff == 0 && Math.abs(ydiff) < 2) ||
            (ydiff == 0 && Math.abs(xdiff) < 2)) {
                // console.log(`${o.id} has xdiff ${xdiff} and ydiff ${ydiff} from ${obj}`)
            let b = !o.internalData
            o.bgColor = b ? lightUp : lightDown
            o.fgColor = b ? 'black' : 'white'
            // o.text = b ? '⧳' : '⧲'
            o.internalData = b
        }
    })
    output.playStatus.progression = Object.values(output.objects).filter(o => !!o.internalData).length / Object.values(output.objects).length
    if (output.playStatus.progression === 1) {
        output.playStatus.status = 'win'
        Object.values(output.objects).forEach(o => o.events = [])
    }
    return output
}