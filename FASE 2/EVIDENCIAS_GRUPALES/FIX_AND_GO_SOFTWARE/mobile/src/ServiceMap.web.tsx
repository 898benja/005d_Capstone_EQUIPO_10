import { createElement, useEffect, useRef, useState } from 'react';
import { Text, View } from 'react-native';
import { apiUrl } from './api';
import { handleMapMessage, MapProps } from './map-contract';

export default function ServiceMap(props: MapProps) {
  const frame = useRef<HTMLIFrameElement>(null);
  const [loaded, setLoaded] = useState(false);
  const url = `${apiUrl}/map/`;
  useEffect(() => {
    if (!apiUrl) return;
    const origin = new URL(apiUrl).origin;
    const receive = (e: MessageEvent) => {
      if (e.source === frame.current?.contentWindow && e.origin === origin) handleMapMessage(e.data, props);
    };
    window.addEventListener('message', receive);
    if (loaded) frame.current?.contentWindow?.postMessage({type:'fixgo-update',point:props.point,markers:props.markers,readOnly:props.readOnly,actionLabel:props.actionLabel,immersive:props.immersive,selectedId:props.selectedId},origin);
    return () => window.removeEventListener('message', receive);
  }, [props.point, props.markers, props.onPoint, props.onSelect, props.readOnly, props.actionLabel, props.immersive, props.selectedId, loaded]);
  if (!apiUrl) return <Text>Configura la conexión para mostrar el mapa.</Text>;
  return <View style={{height:props.height??380,borderRadius:props.immersive?0:18,overflow:'hidden'}}>{createElement('iframe', {
    ref:frame,src:url,title:'Mapa de prestadores FIX&GO',onLoad:()=>setLoaded(true),
    style:{width:'100%',height:'100%',border:0},referrerPolicy:'strict-origin-when-cross-origin',
  })}</View>;
}
