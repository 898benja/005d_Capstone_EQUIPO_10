import { useEffect, useState } from 'react';
import { Text } from 'react-native';
import { api, Session } from './api';
import { Button, Card, s } from './ui';
import type { Run } from './screens';

export function DemoWallet({session,run,busy}:{session:Session;run:Run;busy:boolean}) {
  const [card,setCard]=useState<{brand:string;last4:string}|null>(null);
  const [loaded,setLoaded]=useState(false);
  const load=async()=>{const data=await api<{card:typeof card}>('wallet/demo-card/',session.token);setCard(data.card);setLoaded(true);};
  // Abrir a petición evita competir con la carga inicial del perfil.
  return <Card>
    <Text style={s.title}>Mi tarjeta de demostración</Text>
    <Text style={s.body}>Prueba la experiencia de guardar una tarjeta. No ingreses datos bancarios: esta tarjeta es ficticia y no realiza cobros.</Text>
    {!loaded?<Button secondary label="Ver tarjeta de prueba" busy={busy} onPress={()=>void run(load)}/>:
      card?<><Text style={s.title}>{card.brand} · •••• {card.last4}</Text><Button secondary label="Quitar tarjeta de prueba" busy={busy} onPress={()=>void run(async()=>{await api('wallet/demo-card/',session.token,'DELETE',{});await load();})}/></>:
      <Button label="Guardar tarjeta de prueba" busy={busy} onPress={()=>void run(async()=>{await api('wallet/demo-card/',session.token,'POST',{});await load();})}/>}
  </Card>;
}
