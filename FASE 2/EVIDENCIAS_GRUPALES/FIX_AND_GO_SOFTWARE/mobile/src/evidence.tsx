import { useState } from 'react';
import { Image, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { api, Session } from './api';
import { Button, Card, Field, s } from './ui';
import type { Run } from './screens';
type Evidence={id:number;caption:string;created_at:string};

export function EvidencePanel({id,session,status,run,busy}:{id:number;session:Session;status:string;run:Run;busy:boolean}) {
  const [items,setItems]=useState<Evidence[]|null>(null);
  const [caption,setCaption]=useState('');
  const [photos,setPhotos]=useState<Record<number,string>>({});
  const path=`requests/${id}/evidence/`;
  const refresh=async()=>setItems(await api<Evidence[]>(path,session.token));
  async function pick(){
    const result=await ImagePicker.launchImageLibraryAsync({mediaTypes:['images'],base64:true,quality:0.6,allowsEditing:true});
    if(result.canceled)return;
    const image=result.assets[0].base64;
    if(!image||image.length>2800000)throw new Error('Selecciona una foto más pequeña (máximo 2 MB).');
    await api(path,session.token,'POST',{image_base64:image,caption});
    setCaption('');await refresh();
  }
  return <Card>
    <Text style={s.title}>Fotos del trabajo</Text>
    <Text style={s.body}>Comparte el resultado sin incluir rostros, documentos o información personal. Solo tú y la otra persona del servicio pueden ver estas fotos.</Text>
    <Button secondary label="Ver fotos del trabajo" busy={busy} onPress={()=>void run(refresh)}/>
    {items?.length===0&&<Text style={s.body}>Aún no se han adjuntado fotos.</Text>}
    {items?.map(item=><View key={item.id} style={{gap:10}}>
      <Text style={s.body}>{item.caption||'Evidencia del trabajo'} · {new Date(item.created_at).toLocaleDateString('es-CL')}</Text>
      {photos[item.id]?<Image accessibilityLabel={item.caption||'Foto del trabajo'} source={{uri:photos[item.id]}} style={{height:240,width:'100%',borderRadius:12}} resizeMode="contain"/>:
      <Button secondary label="Abrir foto" busy={busy} onPress={()=>void run(async()=>{const photo=await api<{image_base64:string}>(`${path}${item.id}/`,session.token);setPhotos(current=>({...current,[item.id]:`data:image/jpeg;base64,${photo.image_base64}`}));})}/>}
    </View>)}
    {session.user.role==='PROVIDER'&&['IN_PROGRESS','COMPLETED'].includes(status)&&<>
      <Field label="Qué muestra la foto" value={caption} onChangeText={setCaption} maxLength={240}/>
      <Button label="Agregar foto del resultado" busy={busy} onPress={()=>void run(pick)}/>
      <Text style={s.label}>Hasta 10 fotos por trabajo. JPEG, PNG o WebP, máximo 2 MB por foto.</Text>
    </>}
    <Text style={s.body}>Las fotos apoyan la revisión del servicio; por sí solas no confirman que el trabajo esté terminado.</Text>
  </Card>;
}
