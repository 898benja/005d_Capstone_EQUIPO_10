import { useEffect, useState } from 'react';
import { ActivityIndicator, Image, Linking, Pressable, ScrollView, Text, View, useWindowDimensions } from 'react-native';
import { api, options, Option, Page, Provider, Session } from './api';
import { Button, colors, s } from './ui';
import ServiceMap from './ServiceMap';
import { Point } from './map-contract';
import type { Run } from './screens';

export function ProviderPortrait({provider,size=52}:{provider:Provider;size?:number}) {
  return provider.avatar?<Image accessibilityLabel={`Foto de ${provider.display_name}`} source={{uri:provider.avatar}} style={{width:size,height:size,borderRadius:size/2}}/>:
    <View style={{width:size,height:size,borderRadius:size/2,backgroundColor:'#FFF0C3',alignItems:'center',justifyContent:'center'}}><Text style={{fontSize:size*0.4,fontWeight:'800',color:colors.ink}}>{provider.display_name.charAt(0)}</Text></View>;
}
export function ProviderRating({provider}:{provider:Provider}) {
  const count=provider.rating_count??0;
  const rating=provider.avg_rating;
  if(!count||rating==null)return <Text style={{fontSize:14,color:colors.muted}}>Sin reseñas todavía</Text>;
  return <Text accessibilityLabel={`${rating.toFixed(1)} de 5, ${count} reseñas`} style={{fontSize:16,color:'#8A5900',fontWeight:'700'}}>{'★'.repeat(Math.round(rating))}{'☆'.repeat(5-Math.round(rating))} <Text style={{color:colors.ink}}>{rating.toFixed(1)} <Text style={{fontWeight:'400',fontSize:13}}>({count} reseñas)</Text></Text></Text>;
}

export function Explore({session,busy,onChoose}:{session:Session;run:Run;busy:boolean;onChoose:(p:Provider)=>void}) {
  const {height,width}=useWindowDimensions();
  const canvasHeight=Math.max(560,height-155);
  const [point,setPoint]=useState<Point|null>(null);
  const [categories,setCategories]=useState<Option[]>([]);
  const [category,setCategory]=useState(0);
  const [radius,setRadius]=useState(10);
  const [page,setPage]=useState<Page<Provider>|null>(null);
  const [number,setNumber]=useState(1);
  const [selected,setSelected]=useState<number|null>(null);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState('');
  const [retry,setRetry]=useState(0);
  useEffect(()=>{let active=true;options('categories/').then(value=>{if(active)setCategories(value);}).catch(()=>{});return()=>{active=false;};},[]);
  // Cada cambio invalida su respuesta anterior. No se sigue ninguna URL externa de paginación.
  useEffect(()=>{
    let active=true;setLoading(true);setError('');setSelected(null);
    const timer=setTimeout(()=>{
      const q=new URLSearchParams({page:String(number)});
      if(category){const c=categories.find(c=>c.id===category);if(c)q.set('category',c.slug);}
      if(point){q.set('latitude',String(point.latitude));q.set('longitude',String(point.longitude));q.set('radius_km',String(radius));}
      api<Page<Provider>>(`providers/?${q}`,session.token).then(value=>{if(active)setPage(value);}).catch(e=>{if(active){setPage(null);setError(e.message);}}).finally(()=>{if(active)setLoading(false);});
    },250);
    return()=>{active=false;clearTimeout(timer);};
  },[point,category,radius,number,retry]);
  const rows=page?.results??[];
  const chosen=rows.find(p=>p.id===selected);
  const markers=rows.filter(p=>p.map_visible&&p.latitude!=null&&p.longitude!=null).map(p=>({id:p.id,name:p.display_name,description:p.categories.map(c=>c.name).join(' · '),latitude:p.latitude!,longitude:p.longitude!}));
  const choosePoint=(value:Point)=>{setPage(null);setPoint(value);setNumber(1);};
  const inset=width>700?28:14;
  const panelWidth=width>800?430:undefined;
  return <View style={{height:canvasHeight,backgroundColor:'#E6EAE7'}}>
    <ServiceMap immersive height={canvasHeight} point={point} markers={markers} selectedId={selected} onPoint={choosePoint} onSelect={setSelected}/>
    <View pointerEvents="box-none" style={{position:'absolute',top:16,left:inset,right:inset,gap:10}}>
      <View style={{backgroundColor:'white',borderRadius:20,padding:16,boxShadow:'0 3px 18px #122f3a18',gap:4,maxWidth:480}}>
        <Text style={{fontSize:12,fontWeight:'800',color:colors.muted,letterSpacing:1}}>SERVICIOS PARA TU HOGAR · SANTIAGO</Text>
        <Text style={{fontSize:22,fontWeight:'800',color:colors.ink}}>{point?'Ayuda cerca de este punto':'¿Dónde necesitas ayuda?'}</Text>
        <Text style={{fontSize:14,color:colors.muted}}>Toca el mapa para indicar la ubicación del servicio</Text>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8}}>
        {[{id:0,name:'Todos'},...categories].map(c=><Pressable key={c.id} accessibilityRole="button" accessibilityState={{selected:category===c.id}} onPress={()=>{setCategory(c.id);setNumber(1);setPage(null);}} style={{paddingHorizontal:18,paddingVertical:13,borderRadius:24,backgroundColor:category===c.id?colors.ink:'white'}}><Text style={{fontSize:15,fontWeight:'700',color:category===c.id?'white':colors.ink}}>{c.name}</Text></Pressable>)}
      </ScrollView>
    </View>
    <View style={{position:'absolute',bottom:width>800?18:0,left:width>800?28:0,right:width>800?undefined:0,width:panelWidth,backgroundColor:'white',borderRadius:width>800?24:0,borderTopLeftRadius:28,borderTopRightRadius:28,padding:18,gap:10,boxShadow:'0 -4px 24px #122f3a18'}}>
      <View style={{alignSelf:'center',width:38,height:4,borderRadius:3,backgroundColor:'#DCE4E3'}}/>
      {chosen?<>
        <View style={{flexDirection:'row',alignItems:'center',gap:12}}>
          <ProviderPortrait provider={chosen} size={64}/>
          <View style={{flex:1,gap:4}}><Text style={s.title}>{chosen.display_name}</Text><ProviderRating provider={chosen}/></View>
          <Pressable accessibilityRole="button" accessibilityLabel="Cerrar ficha del prestador" onPress={()=>setSelected(null)} style={{padding:10}}><Text style={{fontSize:14,fontWeight:'700'}}>Cerrar</Text></Pressable>
        </View>
        <Text style={{fontSize:14,fontWeight:'700',color:colors.ink}}>{chosen.categories.map(c=>c.name).join(' · ')}{chosen.distance_km!=null?` · ${chosen.distance_km} km`:''}</Text>
        <ScrollView style={{maxHeight:90}}><Text style={{fontSize:16,color:colors.muted,lineHeight:23}}>{chosen.description||'Este prestador todavía no agregó una descripción.'}</Text></ScrollView>
        <Button label="Solicitar una cotización" disabled={busy} onPress={()=>onChoose({...chosen,...(point?{requested_point:point}:{})})}/>
      </>:<>
        <View style={{flexDirection:'row',alignItems:'center',gap:10}}><Text style={s.title}>{loading?'Buscando…':point?'Prestadores cerca de ti':'Elige un prestador'}</Text>{loading&&<ActivityIndicator color={colors.ink}/>}</View>
        {!!error?<><Text style={{color:'#842E22'}}>{error}</Text><Button secondary label="Volver a intentar" onPress={()=>setRetry(retry+1)}/></>:<>
          <Text style={{fontSize:14,color:colors.muted}}>{rows.length?'Toca su marcador o desliza las tarjetas.':loading?'Buscamos servicios para tu hogar.':'Sin resultados. Prueba otra zona o especialidad.'}</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:10}}>
            {rows.map(p=><Pressable key={p.id} accessibilityRole="button" accessibilityLabel={`Ver perfil de ${p.display_name}`} onPress={()=>setSelected(p.id)} style={{width:240,borderWidth:1,borderColor:'#DCE4E3',borderRadius:16,padding:12,gap:7}}><View style={{flexDirection:'row',gap:10,alignItems:'center'}}><ProviderPortrait provider={p} size={40}/><Text style={{fontSize:16,fontWeight:'800',color:colors.ink,flex:1}} numberOfLines={1}>{p.display_name}</Text></View><ProviderRating provider={p}/><Text style={{fontSize:13,color:colors.muted}} numberOfLines={1}>{p.categories.map(c=>c.name).join(' · ')}{p.distance_km!=null?` · ${p.distance_km} km`:''}</Text></Pressable>)}
          </ScrollView>
          <View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between'}}>
            <Pressable accessibilityRole="button" onPress={()=>{setRadius(radius===10?20:radius===20?30:10);setNumber(1);setPage(null);}} style={{paddingVertical:10}}><Text style={{fontSize:14,fontWeight:'700'}}>Radio: {radius} km · Cambiar</Text></Pressable>
            {number>1&&<Pressable accessibilityRole="button" onPress={()=>setNumber(number-1)} style={{padding:10}}><Text>Anterior</Text></Pressable>}
            {page?.next&&<Pressable accessibilityRole="button" onPress={()=>setNumber(number+1)} style={{padding:10}}><Text>Siguientes</Text></Pressable>}
          </View>
        </>}
      </>}
      <Text style={{fontSize:12,color:colors.muted}}>Zonas publicadas · Sin seguimiento en vivo</Text>
      <Text accessibilityRole="link" onPress={()=>void Linking.openURL("https://www.openstreetmap.org/copyright")} style={{fontSize:12,color:colors.ink,textDecorationLine:"underline"}}>© OpenStreetMap contributors</Text>
    </View>
  </View>;
}
