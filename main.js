
var map;

var vectorLayer, vectorLayerSource;
var previewLayer, previewLayerSource;

var selectedStation = null;
var popup;

var iconWifiPreview, iconWifiSelected;

window.addEventListener('load', () => {
    map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([37.41, 8.82]),
            zoom: 4
        })
    })


    vectorLayerSource = new ol.source.Vector({});
    vectorLayer = new ol.layer.Vector({
        source: vectorLayerSource
    });
    map.addLayer(vectorLayer);

    previewLayerSource = new ol.source.Vector({});
    previewLayer = new ol.layer.Vector({
        source: previewLayerSource
    });
    map.addLayer(previewLayer);



    popup = new ol.Overlay({
        element: document.getElementById('popup'),
        autoPan: true,
        autoPanAnimation: {
            duration: 250
        },
        offset: [10, 10]
    });

    map.addOverlay(popup);




    map.on('click', evt => {
        let f = map.forEachFeatureAtPixel(
            evt.pixel,
            function (ft, layer) { return ft; }
        );
        if (f && f.get('type') === 'station') {
            showStationPopup(f.get('data'));
        } else {
            console.log(f.type)
        }
    });

    map.on('pointermove', e => {
        if (e.dragging) {
            popup.setPosition(undefined);
            return;
        }

        var pixel = map.getEventPixel(e.originalEvent);
        var hit = map.hasFeatureAtPixel(pixel);

        document.body.style.cursor = hit ? 'pointer' : '';
    });

    map.on('moveend', e => {
        reloadData();
    })



    iconWifiPreview = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 46],
            anchorXUnits: 'fraction',
            anchorYUnits: 'pixels',
            src: 'res/wifi_preview.png'
        })
    });

    iconWifiSelected = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 46],
            anchorXUnits: 'fraction',
            anchorYUnits: 'pixels',
            src: 'res/wifi_selected.png'
        })
    });
});

class StationData {
    constructor(jsonData, preview = false) {
        this.info = jsonData;
        this.preview = preview;
    }

    getHTML() {
        return 'Lat: ' + this.info.lat + '<br>'
            + 'Lon: ' + this.info.lon + '<br>';
    }

    getDetailHTML() {
        return 'MAC Address: ' + this.info.mac + '<br>'
            + 'Latitude: ' + this.info.lat + '<br>'
            + 'Longitude: ' + this.info.lon + '<br>'
            + 'Times seen: ' + this.info.times_seen + '<br>'
    }
}




function showStationPopup(data) {
    popup.setPosition(ol.proj.fromLonLat([data.info.lon, data.info.lat]));
    $('#popup-title').html(data.info.ssid);
    $('#popup-subtitle').html(data.info.mac);
    $('#popup-text').html(data.getHTML())
    $('#popup-link').html('Details');
    $('#popup-link').unbind('click').click(evt => {
        $('#modal-details-title').html(data.info.ssid)
        $('#modal-details-text').html(data.getDetailHTML())
        $('#modal-details').modal('show');
        popup.setPosition(undefined);
    })
    selectedStation = data;
}

function addMarker(data) {
    console.log("Adding marker")
    let feature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([data.info.lon, data.info.lat])),
        type: 'station',
        data
    });


    data.marker = feature;

    if (data.preview) {
        previewLayerSource.addFeature(feature);
    }else{
        //feature.setStyle(iconWifiPreview);
        vectorLayerSource.addFeature(feature);
    }



}

function loadPreviewFile() {
    file = document.getElementById('modal-preview-fileselector').files[0];

    var fileReader = new FileReader();
    fileReader.onload = function (fileLoadedEvent) {
        var text = fileLoadedEvent.target.result;
        let jsonData = JSON.parse(text);
        var data;
        for (let i = 0; i < jsonData['data'].length; i++) {
            data = new StationData(jsonData['data'][i], preview = true);
            addMarker(data);
        }
        map.getView().setCenter(ol.proj.fromLonLat([data.info.lon, data.info.lat]));
        map.getView().setZoom(15);

    };

    fileReader.readAsText(file);
}

function reloadData(){
    console.log("Loading data...");
    let extent = map.getView().calculateExtent(map.getSize());
    var box = ol.proj.transformExtent(extent, 'EPSG:3857', 'EPSG:4326')
    requestData(box[1], box[3], box[0], box[2])
}

function requestData(latMin, latMax, lonMin, lonMax) {
    var req = new XMLHttpRequest();
    req.addEventListener("load", () => {
        vectorLayerSource.clear();
        data = JSON.parse(req.responseText);
        data['data'].forEach(sta => {
            let station = new StationData(sta);
            addMarker(station);
        });
    });
    data = {
        area: {
            lat: {
                min: latMin,
                max: latMax
            },
            lon: {
                min: lonMin,
                max: lonMax
            }
        }
    }
    req.open('GET', 'https://traum.me/aws/get?data=' + JSON.stringify(data));
    req.send();
}

function uploadStation(data) {
    var req = new XMLHttpRequest();
    req.addEventListener("load", () => {
        if (req.responseText === 'sucess') {
            upload.done += 1;
            let perc = (upload.done / upload.total) * 100;
            console.log(perc)
            document.getElementById('modal-upload-progress').setAttribute('aria-valuenow', perc);
            document.getElementById('modal-upload-progress').setAttribute('style', 'width:' + Number(perc) + '%');
        } else {
            console.log(req.responseText)
        }
    });
    req.open('GET', 'https://traum.me/aws/add?data=' + JSON.stringify(data));
    req.send();
}

var upload = {
    total: 0,
    done: 0
}

function uploadFile() {
    file = document.getElementById('modal-upload-fileselector').files[0];
    var fileReader = new FileReader();
    fileReader.onload = function (fileLoadedEvent) {
        var text = fileLoadedEvent.target.result;
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", "https://traum.me/aws/upload");
        xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xmlhttp.send(text)
    };

    fileReader.readAsText(file);
}