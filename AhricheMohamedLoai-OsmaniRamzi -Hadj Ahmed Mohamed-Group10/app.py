from flask import Flask, request, render_template, redirect, url_for
import xml.dom.minidom as dom
import xml.etree.ElementTree as ET

app = Flask(__name__)

# ─── Load XML ───────────────────────────────────────────────────
dom_tree = dom.parse('transport.xml')
et_tree  = ET.parse('transport.xml')
root     = et_tree.getroot()

# Station names dict  {id: name}
stations = {s.get('id'): s.get('name')
            for s in root.find('stations').findall('station')}

# ─── Helpers ────────────────────────────────────────────────────

def get_all_trips():
    """Return all trips as list of dicts (for home page)."""
    trips = []
    for line in root.find('lines').findall('line'):
        dep = stations[line.get('departure')]
        arr = stations[line.get('arrival')]
        for t in line.find('trips').findall('trip'):
            s = t.find('schedule')
            classes = [{'type': c.get('type'), 'price': c.get('price')}
                       for c in t.findall('class')]
            trips.append({
                'line_code': line.get('code'),
                'trip_code': t.get('code'),
                'type':      t.get('type'),
                'departure': dep,
                'arrival':   arr,
                'dep_time':  s.get('departure'),
                'arr_time':  s.get('arrival'),
                'classes':   classes,
            })
    return trips


# ─── DOM: Search by code ─────────────────────────────────────────
def search_by_code(code):
    for trip in dom_tree.getElementsByTagName('trip'):
        if trip.getAttribute('code') == code:
            line  = trip.parentNode.parentNode
            sched = trip.getElementsByTagName('schedule')[0]
            classes = [(c.getAttribute('type'), c.getAttribute('price'))
                       for c in trip.getElementsByTagName('class')]
            return {
                'code':    code,
                'line':    line.getAttribute('code'),
                'type':    trip.getAttribute('type'),
                'from':    stations[line.getAttribute('departure')],
                'to':      stations[line.getAttribute('arrival')],
                'time':    f"{sched.getAttribute('departure')} - {sched.getAttribute('arrival')}",
                'classes': classes,
            }
    return None


# ─── ElementTree: Filters ────────────────────────────────────────
def filter_cities(dep, arr):
    result = []
    for line in root.find('lines').findall('line'):
        if (stations[line.get('departure')] == dep and
                stations[line.get('arrival')] == arr):
            trips = []
            for t in line.find('trips').findall('trip'):
                s   = t.find('schedule')
                cls = [(c.get('type'), c.get('price')) for c in t.findall('class')]
                trips.append({
                    'code': t.get('code'), 'type': t.get('type'),
                    'time': f"{s.get('departure')} - {s.get('arrival')}",
                    'classes': cls,
                })
            result.append({'line': line.get('code'), 'trips': trips})
    return result


def filter_type(ttype):
    result = []
    for line in root.find('lines').findall('line'):
        for t in line.find('trips').findall('trip'):
            if t.get('type') == ttype:
                s   = t.find('schedule')
                cls = [(c.get('type'), c.get('price')) for c in t.findall('class')]
                result.append({
                    'line': line.get('code'), 'code': t.get('code'),
                    'type': ttype,
                    'time': f"{s.get('departure')} - {s.get('arrival')}",
                    'classes': cls,
                })
    return result


def filter_price(maxp):
    try:
        maxp = int(maxp)
    except (ValueError, TypeError):
        return []
    result = []
    for line in root.find('lines').findall('line'):
        for t in line.find('trips').findall('trip'):
            valid = [(c.get('type'), c.get('price'))
                     for c in t.findall('class') if int(c.get('price')) <= maxp]
            if valid:
                s = t.find('schedule')
                result.append({
                    'line': line.get('code'), 'code': t.get('code'),
                    'type': t.get('type'),
                    'time': f"{s.get('departure')} - {s.get('arrival')}",
                    'classes': valid,
                })
    return result


# ─── ElementTree: Statistics ─────────────────────────────────────
def get_stats():
    line_stats  = []
    types_count = {}
    for line in root.find('lines').findall('line'):
        lcode = line.get('code')
        dep   = stations[line.get('departure')]
        arr   = stations[line.get('arrival')]
        min_p, max_p = float('inf'), 0
        min_info = max_info = None

        for t in line.find('trips').findall('trip'):
            # count per type
            types_count[t.get('type')] = types_count.get(t.get('type'), 0) + 1
            for c in t.findall('class'):
                p = int(c.get('price'))
                if p < min_p:
                    min_p    = p
                    min_info = (t.get('code'), c.get('type'), p)
                if p > max_p:
                    max_p    = p
                    max_info = (t.get('code'), c.get('type'), p)

        line_stats.append({
            'line':  lcode,
            'dep':   dep,
            'arr':   arr,
            'cheap': min_info,
            'exp':   max_info,
        })
    return line_stats, types_count


# ─── Routes ──────────────────────────────────────────────────────

@app.route('/')
def home():
    trips       = get_all_trips()
    all_types   = list({t['type'] for t in trips})
    return render_template('home.html',
                           trips=trips,
                           total_lines=len({t['line_code'] for t in trips}),
                           total_trips=len(trips),
                           total_types=len(all_types))


@app.route('/search', methods=['GET', 'POST'])
def search():
    trip, code, searched = None, '', False
    if request.method == 'POST':
        code     = request.form.get('code', '').strip().upper()
        trip     = search_by_code(code)
        searched = True
    return render_template('search.html', trip=trip, code=code, searched=searched)


@app.route('/cities', methods=['GET', 'POST'])
def cities():
    city_list = sorted(set(stations.values()))
    data, dep, arr, searched = [], '', '', False
    if request.method == 'POST':
        dep      = request.form.get('dep', '')
        arr      = request.form.get('arr', '')
        data     = filter_cities(dep, arr)
        searched = True
    return render_template('cities.html',
                           cities=city_list, data=data,
                           dep=dep, arr=arr, searched=searched)


@app.route('/type', methods=['GET', 'POST'])
def by_type():
    trips      = get_all_trips()
    all_types  = sorted(set(t['type'] for t in trips))
    data, selected_type, searched = [], '', False
    if request.method == 'POST':
        selected_type = request.form.get('type', '')
        data          = filter_type(selected_type)
        searched      = True
    return render_template('type.html',
                           train_types=all_types, data=data,
                           selected_type=selected_type, searched=searched)


@app.route('/price', methods=['GET', 'POST'])
def by_price():
    data, maxp, searched = [], '', False
    if request.method == 'POST':
        maxp     = request.form.get('maxp', '')
        data     = filter_price(maxp)
        searched = True
    return render_template('price.html', data=data, maxp=maxp, searched=searched)


@app.route('/stats')
def stats():
    line_stats, type_counts = get_stats()
    return render_template('stats.html',
                           line_stats=line_stats,
                           type_counts=type_counts)


if __name__ == '__main__':
    app.run(debug=True)
