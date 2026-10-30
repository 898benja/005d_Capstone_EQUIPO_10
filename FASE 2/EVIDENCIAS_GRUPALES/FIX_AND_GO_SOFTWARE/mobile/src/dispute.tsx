import { useState } from 'react';
import { Text } from 'react-native';
import { api, Session } from './api';
import { Button,Card,Field,s } from './ui';
import type { Run } from './screens';
type Dispute={status:'OPEN'|'REJECTED'|'REFUNDED';reason:string;review_note:string};
export function DisputePanel({id,session,run,busy,refresh}:{id:number;session:Session;run:Run;busy:boolean;refresh:()=>Promise<void>}) {
  const [item,setItem]=useState<Dispute|null>(null);
  const [loaded,setLoaded]=useState(false);
  const [reason,setReason]=useState('');
  const path=`requests/${id}/dispute/`;
  const load=async()=>{setItem(await api<Dispute|null>(path,session.token));setLoaded(true);await refresh();};
  return <Card>
    <Text style={s.title}>Ayuda con este trabajo</Text>
    <Text style={s.body}>Si el trabajo no se realizó, informa lo ocurrido. El equipo revisará los antecedentes antes de resolver el reembolso y una posible alerta.</Text>
    <Button secondary label="Consultar estado del reclamo" busy={busy} onPress={()=>void run(load)}/>
    {item?<><Text style={s.title}>{{OPEN:'En revisión',REJECTED:'Reclamo rechazado',REFUNDED:'Reembolso de demostración aprobado'}[item.status]}</Text><Text style={s.body}>{item.reason}</Text>{!!item.review_note&&<Text style={s.body}>{item.review_note}</Text>}</>:
      loaded&&session.user.role==='CLIENT'?<>
        <Field label="Cuéntanos qué ocurrió" multiline maxLength={2000} value={reason} onChangeText={setReason}/>
        <Button label="Enviar reclamo para revisión" busy={busy} disabled={reason.trim().length<10} onPress={()=>void run(async()=>{await api(path,session.token,'POST',{reason:reason.trim()});setReason('');await load();})}/>
      </>:loaded&&<Text style={s.body}>No hay un reclamo registrado.</Text>}
  </Card>;
}
