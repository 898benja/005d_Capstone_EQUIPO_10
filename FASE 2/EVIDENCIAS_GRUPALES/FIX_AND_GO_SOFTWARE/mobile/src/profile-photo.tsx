import { Text } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { api, Provider, Session } from './api';
import { Button,s } from './ui';
import { ProviderPortrait } from './explore-map';
import type { Run } from './screens';
export function ProfilePhoto({profile,session,run,busy,onPhoto}:{profile:Provider;session:Session;run:Run;busy:boolean;onPhoto:(avatar:string)=>void}) {
  return <>
    <Text style={s.title}>Tu foto de perfil</Text>
    <ProviderPortrait provider={profile} size={80}/>
    <Text style={s.body}>Esta foto será visible para los clientes junto a tu descripción y tus valoraciones.</Text>
    <Button secondary label={profile.avatar?'Cambiar foto de perfil':'Agregar foto de perfil'} busy={busy} onPress={()=>void run(async()=>{
      const result=await ImagePicker.launchImageLibraryAsync({mediaTypes:['images'],base64:true,allowsEditing:true,aspect:[1,1],quality:0.6});
      if(result.canceled)return;
      const image=result.assets[0].base64;
      if(!image||image.length>2800000)throw new Error('Selecciona una imagen de hasta 2 MB.');
      const data=await api<{avatar:string}>('auth/me/provider-profile/avatar/',session.token,'POST',{image_base64:image});onPhoto(data.avatar);
    })}/>
    {!!profile.avatar&&<Button secondary label="Quitar foto" busy={busy} onPress={()=>void run(async()=>{await api('auth/me/provider-profile/avatar/',session.token,'DELETE',{});onPhoto('');})}/>}
  </>;
}
