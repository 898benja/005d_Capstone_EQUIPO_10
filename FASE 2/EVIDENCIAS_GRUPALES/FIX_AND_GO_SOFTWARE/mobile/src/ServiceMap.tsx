import { useEffect, useRef, useState } from 'react';
import { Text, View } from 'react-native';
import { WebView } from 'react-native-webview';
import { apiUrl } from './api';
import { handleMapMessage, MapProps } from './map-contract';

export default function ServiceMap(props: MapProps) {
  const frame=useRef<WebView>(null);
  const [ready,setReady]=useState(false);
  const [failed,setFailed]=useState(false);
  const url=`${apiUrl}/map/`;
  useEffect(()=>{
    if(ready) frame.current?.injectJavaScript(`window.fixgoUpdate&&window.fixgoUpdate(${JSON.stringify({type:'fixgo-update',point:props.point,markers:props.markers,readOnly:props.readOnly,actionLabel:props.actionLabel,immersive:props.immersive,selectedId:props.selectedId}).replace(/</g,'\\u003c')});true;`);
  },[ready,props.point,props.markers,props.readOnly,props.actionLabel,props.immersive,props.selectedId]);
  if(!apiUrl||failed)return <Text>Mapa no disponible. Usa las coordenadas y el listado.</Text>;
  return <View style={{height:props.height??380,borderRadius:props.immersive?0:18,overflow:'hidden'}}><WebView
    ref={frame} source={{uri:url}} userAgent="FixGo-MVP/1.0 (+https://github.com/898benja/fix-and-go)"
    onLoadEnd={()=>setReady(true)} onError={()=>setFailed(true)}
    onHttpError={()=>setFailed(true)} cacheEnabled javaScriptEnabled
    onShouldStartLoadWithRequest={r=>r.url===url||r.url==='about:blank'}
    onMessage={e=>handleMapMessage(e.nativeEvent.data,props)}
  /></View>;
}
