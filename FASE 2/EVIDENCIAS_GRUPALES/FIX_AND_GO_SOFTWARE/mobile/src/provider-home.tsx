import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { api, Session } from './api';
import { Button, Card, colors, s } from './ui';
import ServiceMap from './ServiceMap';
import { validPoint } from './map-contract';
import type { Run } from './screens';

type Job = {id:number;client_name:string;category_name:string;commune_name:string;status:string;status_display:string;latitude:number|null;longitude:number|null};
type Dashboard = {warning_count:number;counts:Record<string,number>;recent:Job[];customers:{id:number;name:string;completed_jobs:number}[]};
export function ProviderHome({session,run,busy,onOpen}:{session:Session;run:Run;busy:boolean;onOpen:(id:number)=>void}) {
  const [data,setData]=useState<Dashboard|null>(null);
  const load=()=>run(async()=>setData(await api<Dashboard>('provider/dashboard/',session.token)));
  useEffect(()=>{void load();},[]);
  const markers=(data?.recent??[]).filter(validPoint).map(job=>({
    id:job.id,name:job.client_name,description:`${job.category_name} · ${job.status_display}`,
    latitude:job.latitude!,longitude:job.longitude!,
  }));
  return <>
    <Text style={s.label}>TU ESPACIO DE TRABAJO</Text>
    <Text style={s.heading}>Hola, {session.user.first_name || 'prestador'}</Text>
    <Text style={s.body}>Revisa tus solicitudes y organiza tu día en Santiago.</Text>
    {!!data?.warning_count&&<Card><Text style={s.title}>Alertas confirmadas: {data.warning_count} de 3</Text><Text style={s.body}>Revisa la resolución en el servicio correspondiente. Con tres incumplimientos confirmados se deshabilita la cuenta.</Text></Card>}
    <View style={{flexDirection:'row',gap:10,flexWrap:'wrap'}}>
      {[
        ['Por cotizar',data?.counts.PENDING??0],
        ['En curso',(data?.counts.ACCEPTED??0)+(data?.counts.IN_PROGRESS??0)],
        ['Terminados',data?.counts.COMPLETED??0],
      ].map(([label,count])=><View key={label} style={{flex:1,minWidth:95,padding:16,borderRadius:18,backgroundColor:'white',gap:6}}>
        <Text style={{fontSize:30,fontWeight:'800',color:colors.ink}}>{count}</Text><Text style={s.body}>{label}</Text>
      </View>)}
    </View>
    <Button secondary label="Actualizar mi inicio" busy={busy} onPress={()=>void load()}/>
    <Text style={s.title}>Tus trabajos en Santiago</Text>
    <Text style={s.body}>Solo aparecen ubicaciones de solicitudes asignadas a ti. Toca un marcador para ver el trabajo.</Text>
    <ServiceMap point={null} markers={markers} onPoint={()=>{}} onSelect={onOpen} readOnly actionLabel="Ver trabajo"/>
    {!markers.length&&<Text style={s.body}>Tus solicitudes con ubicación aparecerán aquí.</Text>}
    <Text style={s.title}>Trabajos recientes</Text>
    {data?.recent.map(job=><Card key={job.id}>
      <Text style={s.label}>{job.status_display} · #{job.id}</Text>
      <Text style={s.title}>{job.category_name}</Text>
      <Text style={s.body}>{job.client_name} · {job.commune_name}</Text>
      <Button label="Ver trabajo" onPress={()=>onOpen(job.id)} disabled={busy}/>
    </Card>)}
    {data&&!data.recent.length&&<Card><Text style={s.body}>Aún no recibes solicitudes. Completa tu perfil y publica tu zona de atención para que puedan encontrarte.</Text></Card>}
    <Text style={s.title}>Clientes que atendiste</Text>
    {data?.customers.map(customer=><Card key={customer.id}><Text style={s.title}>{customer.name}</Text><Text style={s.body}>{customer.completed_jobs} trabajos terminados contigo</Text></Card>)}
    {data&&!data.customers.length&&<Text style={s.body}>Aquí verás a tus clientes después de terminar sus servicios.</Text>}
    <Text style={s.label}>Se muestran hasta 20 trabajos y clientes. Revisa Solicitudes para ver el historial.</Text>
  </>;
}
