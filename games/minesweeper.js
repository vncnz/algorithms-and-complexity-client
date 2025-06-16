let bgMine = 'hsl(0, 80%, 50%)'
let bgFlag = 'hsl(0, 80%, 80%)'
let bgGray = "hsl(0, 0%, 80%)"
let bgGreen = "hsl(100, 80%, 80%)"

export const createDefinitionForMinesweeperGame = () => {
    let sz = 4
    let mines = []
    let num_mines = 2
    let sec = sz * sz // security
    while (mines.length <= num_mines && --sec > 0) {
        let rand = parseInt(Math.random() * sz * sz)
        if (!mines.includes(rand)) mines.push(rand)
    }
    let game = {
        field: {
            xsize: sz,
            ysize: sz
        },
        playStatus: {
            status: 'running',
            progression: 0,
            internalData: { mines }
        },
        objects: {},
        events: {}
    }

    for(let i = 0; i < sz; i++) {
        for(let j = 0; j < sz; j++) {
            let id = j*sz + i
            // let b = game.playStatus.internalData.mines.includes(id)
            game.objects[id] = {
                id,
                bgColor: bgGray,
                fgColor: 'black',
                rect: { x: i, y: j, w: 1, h: 1 },
                // text: b ? '⧳' : '⧲',
                text: `O`,
                internalData: { status: 'untouched', mine: mines.includes(id) }
            }
            game.events[id] = [ 'click', 'contextmenu' ]
        }
    }
    game.playStatus.progression = 1 - (Object.values(game.objects).filter(o => !!o.internalData).length / Object.values(game.objects).length)
    return game
}

export const simulateServerForMinesweeperGame = (objs, evtType, input) => {
    console.warn('Simulating server input', objs, evtType, input)
    let output = JSON.parse(JSON.stringify(input)) // simulo una comunicazione col server quindi non modifico l'oggetto corrente, ovviamente!
    let objid = objs[0]
    let obj = output.objects[objid]

    let isLeftClick = evtType === 'contextmenu'
    if (isLeftClick) {
        console.log('isLeftClick', isLeftClick)
        if (obj.internalData.status == 'flag') obj.internalData.status = 'untouched'
        else obj.internalData.status = 'flag'
    } else {
        obj.internalData.status = 'seen'
    }

    if (obj.internalData.status == 'seen') {
        if (obj.internalData.mine) {
            output.playStatus.status = 'lose'
            // Object.values(output.objects).forEach(o => o.events = [])
            output.events[id] = []
        }
    }

    if (output.playStatus.status == 'lose') {
        Object.values(output.objects).forEach(obj => {
            obj.internalData.status = 'seen'
        })
    }

    drawField(output)

    output.playStatus.progression = (Object.values(output.objects).filter(o => o.internalData.status !== 'untouched').length / (Object.values(output.objects).length))
    if (output.playStatus.status != 'lose' && output.playStatus.progression === 1) {
        output.playStatus.status = 'win'
        // Object.values(output.objects).forEach(o => o.events = [])
        output.events = []
    }
    console.warn('Simulating server output', output)
    return output
}

const getNeighbors = (id, row) => {
    let r = Math.floor(id / row)
    let c = id % row

    const directions = [
        [-1, -1], [-1, 0], [-1, 1],
        [ 0, -1],          [ 0, 1],
        [ 1, -1], [ 1, 0], [ 1, 1]
    ]

    return directions
        .map(([dr, dc]) => {
            const newRow = r + dr;
            const newCol = c + dc;

            // Calcola il nuovo id
            return newRow >= 0 && newRow < row && newCol >= 0 && newCol < row
                ? newRow * row + newCol
                : null; // Fuori dai limiti
        })
        .filter(id => id !== null)
}

const countMines = (id, board) => {
    let neigh = getNeighbors(id, board.field.xsize)
    return Object.values(board.objects).filter(o => {
        let isNeigh = neigh.includes(o.id)
        let isMine = board.playStatus.internalData.mines.includes(o.id)
        return isMine && isNeigh
    }).length
}

const drawField = (output) => {
    Object.values(output.objects).forEach(obj => {
        switch (obj.internalData.status) {
            case 'flag':
                obj.text = '🏴'
                obj.bgColor = bgFlag
                break
            case 'seen':
                if (obj.internalData.mine) {
                    obj.text = 'X'
                    obj.bgColor = bgMine
                } else {
                    let c = countMines(obj.id, output)
                    obj.text = `${c}`
                    obj.bgColor = bgGreen
                }
                break
            default:
                obj.text = 'O'
                obj.bgColor = bgGray
        }
    })
}