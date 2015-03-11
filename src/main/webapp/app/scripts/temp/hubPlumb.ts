/**
 * Created by remoliebi on 07.03.15.
 */

/* tslint:disable */

'use strict';
var hubPlumb = hubPlumb || {};
hubPlumb.connectorPaintStyle = function () {
    return {
        lineWidth: 4,
        strokeStyle: '#61B7CF',
        joinstyle: 'round',
        outlineColor: 'white',
        outlineWidth: 2
    };
};
// .. and this is the hover style.
hubPlumb.connectorHoverStyle = function () {
    return {
        lineWidth: 4,
        strokeStyle: '#216477',
        outlineWidth: 2,
        outlineColor: 'white'
    };
};
hubPlumb.endpointHoverStyle = function () {
    return {
        fillStyle: '#216477',
        strokeStyle: '#216477'
    };
};
hubPlumb.sourceEndpoint = function () {
    return {
        endpoint: 'Dot',
        paintStyle: {
            strokeStyle: '#7AB02C',
            fillStyle: 'transparent',
            radius: 7,
            lineWidth: 3
        },
        isSource: true,
        connector: ['Flowchart', {stub: [40, 60], gap: 10, cornerRadius: 5, alwaysRespectStubs: true}],
        connectorStyle: hubPlumb.connectorPaintStyle(),
        hoverPaintStyle: hubPlumb.endpointHoverStyle(),
        connectorHoverStyle: hubPlumb.connectorHoverStyle(),
        dragOptions: {},
        overlays: [
            ['Label', {
                location: [0.5, 1.5],
                label: 'Label',
                cssClass: 'endpointSourceLabel'
            }]
        ],
        anchor: ['Continuous', {faces: ['bottom']}]
    };
};
// the definition of target endpoints (will appear when the user drags a connection)
hubPlumb.targetEndpoint = function () {
    return {
        endpoint: 'Dot',
        paintStyle: {fillStyle: '#7AB02C', radius: 11},
        hoverPaintStyle: hubPlumb.endpointHoverStyle(),
        maxConnections: -1,
        dropOptions: {hoverClass: 'hover', activeClass: 'active'},
        isTarget: true,
        overlays: [
            ['Label', {location: [0.5, -0.5], label: 'Drop', cssClass: 'endpointTargetLabel'}]
        ],
        anchor: ['Continuous', {faces: ['top']}]
    };

};

hubPlumb.addEndpoints = function (toId, sourceAnchors, targetAnchors, scope, params) {
    for (var i = 0; i < sourceAnchors; i++) {
        var sourceUUID = toId + i + 'source';
        hubPlumb.instance.addEndpoint('flowchart' + toId, hubPlumb.sourceEndpoint(), {anchor: 'Continuous', uuid: sourceUUID, scope: scope, parameters: params});
    }
    for (var j = 0; j < targetAnchors; j++) {
        var targetUUID = toId + j + 'target';
        hubPlumb.instance.addEndpoint('flowchart' + toId, hubPlumb.targetEndpoint(), {anchor: 'Continuous', uuid: targetUUID, scope: scope, parameters: params});
    }
};
