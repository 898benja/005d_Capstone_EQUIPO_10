import { useEffect, useState } from "react";
import { ActivityIndicator, Modal, Text, View } from "react-native";
import {
  api,
  options,
  Option,
  Page,
  Provider,
  Rating,
  RequestItem,
  Session,
  User,
} from "./api";
import { Button, Card, Chips, colors, Field, s } from "./ui";
import { BillingPanel, loadBilling, BillingData } from "./billing";
import ServiceMap from './ServiceMap';
import { DemoWallet } from './wallet';
import { EvidencePanel } from './evidence';
import { DisputePanel } from './dispute';
import { ProfilePhoto } from './profile-photo';
export { Explore } from './explore-map';
export type Run = (job: () => Promise<void>) => Promise<void>;
export const money = (value: number) => `$${value.toLocaleString("es-CL")}`;

export function Access({
  run,
  busy,
  onSession,
}: {
  run: Run;
  busy: boolean;
  onSession: (session: Session) => Promise<void>;
}) {
  const [register, setRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [first, setFirst] = useState("");
  const [last, setLast] = useState("");
  const [display, setDisplay] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [areas, setAreas] = useState<Option[]>([]);
  const [commune, setCommune] = useState<number | null>(null);
  useEffect(() => {
    if (register) void run(async () => setAreas(await options("communes/")));
  }, [register]);
  const [role, setRole] = useState<"CLIENT" | "PROVIDER">("CLIENT");
  return (
    <>
      <View style={s.hero}>
        <Text
          style={{ color: colors.yellow, fontWeight: "700", letterSpacing: 2 }}
        >
          TU HOGAR, EN BUENAS MANOS
        </Text>
        <Text
          style={[s.heading, { color: "white", fontSize: 36, lineHeight: 42 }]}
        >
          {"Una solución.\nA un toque."}
        </Text>
        <Text style={{ color: "#C8D8D9", lineHeight: 22 }}>
          Encuentra servicios para tu hogar y sigue cada paso desde tu celular.
        </Text>
        <Text style={{ color: colors.yellow, fontSize: 12 }}>
          SANTIAGO · MVP ACADÉMICO
        </Text>
      </View>
      <Card>
        <Text style={s.title}>
          {register ? "Crea tu cuenta" : "Qué bueno verte"}
        </Text>
        <Text style={s.body}>
          {register
            ? "Elige cómo quieres usar FIX&GO."
            : "Ingresa para continuar con tus servicios."}
        </Text>
        {register && (
          <>
            <Chips
              items={[
                { id: 0, name: "Necesito un servicio" },
                { id: 1, name: "Ofrezco servicios" },
              ]}
              selected={[role === "CLIENT" ? 0 : 1]}
              onSelect={(id) => setRole(id === 0 ? "CLIENT" : "PROVIDER")}
            />
            <Field
              label="Nombre"
              value={first}
              onChangeText={setFirst}
              autoComplete="given-name"
            />
            <Field
              label="Apellido"
              value={last}
              onChangeText={setLast}
              autoComplete="family-name"
            />
            <Field label="Teléfono (opcional)" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
            <Field label="Dirección habitual (opcional)" value={address} onChangeText={setAddress} />
            <Text style={s.label}>Comuna habitual (opcional)</Text>
            <Chips items={areas} selected={commune ? [commune] : []} onSelect={v => setCommune(v === commune ? null : v)} />
            <Text style={s.body}>Puedes completar estos datos ahora o guardarlos después en Mi perfil.</Text>
            {role === "PROVIDER" && (
              <Field
                label="Nombre de tu servicio"
                value={display}
                onChangeText={setDisplay}
              />
            )}
          </>
        )}
        <Field
          label="Correo electrónico"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          autoComplete="email"
          placeholder="tu@correo.cl"
        />
        <Field
          label="Contraseña"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          autoCapitalize="none"
          autoComplete={register ? "new-password" : "current-password"}
        />
        <Button
          label={register ? "Crear cuenta" : "Ingresar"}
          busy={busy}
          disabled={
            !email.trim() ||
            !password ||
            (register &&
              (!first.trim() ||
                !last.trim() ||
                (role === "PROVIDER" && !display.trim())))
          }
          onPress={() =>
            void run(async () => {
              const session = await api<Session>(
                `auth/${register ? "register" : "login"}/`,
                undefined,
                "POST",
                {
                  email: email.trim(),
                  password,
                  ...(register
                    ? {
                        first_name: first.trim(),
                        last_name: last.trim(),
                        role,
                        ...(role === "PROVIDER" ? {display_name: display.trim()} : {}),
                        phone: phone.trim(), default_address: address.trim(), default_commune: commune,
                      }
                    : {}),
                },
              );
              await onSession(session);
            })
          }
        />
        <Button
          secondary
          disabled={busy}
          label={register ? "Ya tengo una cuenta" : "Crear una cuenta"}
          onPress={() => setRegister(!register)}
        />
      </Card>
    </>
  );
}

export function NewRequest({
  provider,
  session,
  run,
  busy,
  onCreated,
}: {
  provider: Provider;
  session: Session;
  run: Run;
  busy: boolean;
  onCreated: (id: number) => void;
}) {
  const [category, setCategory] = useState(provider.categories[0]?.id ?? 0);
  const [commune, setCommune] = useState(provider.communes.find(c => c.id === session.user.default_commune)?.id ?? provider.communes[0]?.id ?? 0);
  const [description, setDescription] = useState("");
  const [address, setAddress] = useState(session.user.default_address ?? "");
  return (
    <>
      <Text style={s.heading}>Cuéntanos qué necesitas</Text>
      <Card>
        <Text style={s.title}>{provider.display_name}</Text>
        <Text style={s.body}>{provider.description}</Text>
        <Text style={s.label}>Servicio</Text>
        <Chips
          items={provider.categories}
          selected={[category]}
          onSelect={setCategory}
        />
        <Text style={s.label}>Comuna de atención</Text>
        <Chips
          items={provider.communes}
          selected={[commune]}
          onSelect={setCommune}
        />
        <Field
          label="Describe el problema"
          multiline
          value={description}
          onChangeText={setDescription}
          placeholder="Por ejemplo: la llave del baño gotea y necesito repararla."
        />
        <Field
          label="Dirección o referencia (opcional)"
          value={address}
          onChangeText={setAddress}
        />
        <Text style={s.body}>
          La dirección se comparte con el prestador asignado. Enviar esta
          solicitud no confirma un precio ni realiza un pago.
        </Text>
        <Button
          label="Solicitar cotización"
          busy={busy}
          disabled={!category || !commune || description.trim().length < 10}
          onPress={() =>
            void run(async () => {
              // La API pide el ID del usuario, no el ID del perfil del prestador.
              const result = await api<RequestItem>(
                "requests/",
                session.token,
                "POST",
                {
                  provider_id: provider.user_id,
                  ...(provider.requested_point ? {latitude:provider.requested_point.latitude,longitude:provider.requested_point.longitude} : {}),
                  category_id: category,
                  commune_id: commune,
                  description: description.trim(),
                  address: address.trim(),
                },
              );
              onCreated(result.id);
            })
          }
        />
      </Card>
    </>
  );
}

export function Requests({
  session,
  run,
  busy,
  onOpen,
}: {
  session: Session;
  run: Run;
  busy: boolean;
  onOpen: (id: number) => void;
}) {
  const [page, setPage] = useState<Page<RequestItem> | null>(null);
  const [number, setNumber] = useState(1);
  const load = (n = 1) =>
    run(async () => {
      setPage(
        await api<Page<RequestItem>>(`requests/?page=${n}`, session.token),
      );
      setNumber(n);
    });
  useEffect(() => {
    void load();
  }, []);
  return (
    <>
      <Text style={s.heading}>
        {session.user.role === "CLIENT"
          ? "Mis solicitudes"
          : "Tu trabajo, al día"}
      </Text>
      <Text style={s.body}>
        {session.user.role === "CLIENT"
          ? "Cotizaciones, avances y próximos pasos."
          : "Responde a tus clientes y gestiona cada servicio."}
      </Text>
      <Button
        secondary
        label="Actualizar solicitudes"
        busy={busy}
        onPress={() => void load(number)}
      />
      {page?.results.length === 0 && (
        <Card>
          <Text style={s.title}>Todo empieza con una solicitud</Text>
          <Text style={s.body}>
            {session.user.role === "CLIENT"
              ? "Busca un especialista y cuéntale lo que necesitas."
              : "Completa tus especialidades y comunas en tu perfil para que puedan encontrarte."}
          </Text>
        </Card>
      )}
      {page?.results.map((item) => (
        <Card key={item.id}>
          <Text style={s.badge}>{item.status_display}</Text>
          <Text style={s.title}>{item.category_name}</Text>
          <Text style={s.body}>{item.description}</Text>
          <Text style={s.label}>
            {session.user.role === "CLIENT"
              ? item.provider_name
              : item.client_name}{" "}
            · {item.commune_name}
          </Text>
          <Button
            secondary
            disabled={busy}
            label={`Ver solicitud #${item.id}`}
            onPress={() => onOpen(item.id)}
          />
        </Card>
      ))}
      {number > 1 && (
        <Button
          secondary
          label="Anterior"
          busy={busy}
          onPress={() => void load(number - 1)}
        />
      )}
      {page?.next && (
        <Button
          secondary
          label="Siguiente"
          busy={busy}
          onPress={() => void load(number + 1)}
        />
      )}
    </>
  );
}

export function Detail({
  id,
  session,
  run,
  busy,
}: {
  id: number;
  session: Session;
  run: Run;
  busy: boolean;
}) {
  const [item, setItem] = useState<RequestItem | null>(null);
  const [rating, setRating] = useState<Rating | null>(null);
  const [billing, setBilling] = useState<BillingData | null>(null);
  const [pendingAction, setPendingAction] = useState<{
    title: string;
    route: string;
  } | null>(null);
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [score, setScore] = useState(5);
  const [comment, setComment] = useState("");
  const refresh = async () => {
    const value = await api<RequestItem>(`requests/${id}/`, session.token);
    setItem(value);
    if (["ACCEPTED", "IN_PROGRESS", "COMPLETED"].includes(value.status)) {
      setBilling(await loadBilling(id, session.token));
    } else setBilling(null);
    if (value.status === "COMPLETED") {
      try {
        setRating(await api<Rating>(`requests/${id}/rating/`, session.token));
      } catch (error) {
        if (
          !(
            error &&
            typeof error === "object" &&
            "status" in error &&
            error.status === 404
          )
        )
          throw error;
        setRating(null);
      }
    }
  };
  useEffect(() => {
    void run(refresh);
  }, [id]);
  const act = (route: string, body: unknown = {}) =>
    run(async () => {
      await api(`requests/${id}/${route}/`, session.token, "POST", body);
      await refresh();
    });
  const confirm = (title: string, route: string) =>
    setPendingAction({ title, route });
  const client = session.user.role === "CLIENT";
  if (!item)
    return (
      <>
        <Text style={s.heading}>Solicitud #{id}</Text>
        {busy ? (
          <ActivityIndicator />
        ) : (
          <Button label="Reintentar" onPress={() => void run(refresh)} />
        )}
      </>
    );
  return (
    <>
      <Text style={s.heading}>Solicitud #{id}</Text>
      {pendingAction && (
        <Modal
          transparent
          animationType="fade"
          onRequestClose={() => setPendingAction(null)}
        >
          <View
            style={{
              flex: 1,
              justifyContent: "center",
              padding: 24,
              backgroundColor: "rgba(18,47,58,0.6)",
            }}
          >
            <Card>
              <Text style={s.title}>{pendingAction.title}</Text>
              <Text style={s.body}>
                Esta decisión actualizará el estado del servicio.
              </Text>
              <Button
                label="Confirmar"
                busy={busy}
                onPress={() => {
                  const target = pendingAction.route;
                  setPendingAction(null);
                  void act(target);
                }}
              />
              <Button
                secondary
                label="Volver sin cambios"
                disabled={busy}
                onPress={() => setPendingAction(null)}
              />
            </Card>
          </View>
        </Modal>
      )}
      <Button
        secondary
        label="Actualizar estado"
        busy={busy}
        onPress={() => void run(refresh)}
      />
      <Card>
        <Text style={s.badge}>{item.status_display}</Text>
        <Text style={s.title}>{item.category_name}</Text>
        <Text style={s.body}>{item.description}</Text>
        <Text style={s.label}>
          {item.provider_name} · {item.commune_name}
        </Text>
        {!!item.address && <Text style={s.body}>{item.address}</Text>}
      </Card>
      {item.quote && (
        <Card>
          <Text style={s.title}>Tu cotización</Text>
          <Text style={[s.heading, { fontSize: 32 }]}>
            {money(item.quote.price)} <Text style={s.body}>CLP</Text>
          </Text>
          <Text style={s.body}>{item.quote.description}</Text>
          {!!item.quote.notes && <Text style={s.body}>{item.quote.notes}</Text>}
          {item.status === "QUOTED" &&
            (client ? (
              <>
                <Button
                  label="Aceptar cotización"
                  busy={busy}
                  onPress={() =>
                    confirm("¿Aceptar esta cotización?", "quote/accept")
                  }
                />
                <Button
                  secondary
                  label="Rechazar cotización"
                  busy={busy}
                  onPress={() =>
                    confirm("¿Rechazar esta cotización?", "quote/reject")
                  }
                />
              </>
            ) : (
              <Button
                secondary
                label="Retirar cotización"
                busy={busy}
                onPress={() =>
                  confirm("¿Retirar la cotización?", "quote/withdraw")
                }
              />
            ))}
        </Card>
      )}
      {!client && item.status === "PENDING" && (
        <Card>
          <Text style={s.title}>Prepara tu propuesta</Text>
          <Field
            label="Trabajo incluido"
            multiline
            value={description}
            onChangeText={setDescription}
          />
          <Field
            label="Precio total en CLP"
            keyboardType="number-pad"
            value={price}
            onChangeText={setPrice}
            placeholder="35000"
          />
          <Button
            label="Enviar cotización"
            busy={busy}
            disabled={
              !description.trim() || !/^\d+$/.test(price) || Number(price) <= 0
            }
            onPress={() =>
              void act("quote", {
                description: description.trim(),
                price: Number(price),
              })
            }
          />
        </Card>
      )}
      {client && ["PENDING", "QUOTED"].includes(item.status) && (
        <Button
          secondary
          label="Cancelar solicitud"
          busy={busy}
          onPress={() => confirm("¿Cancelar la solicitud?", "cancel")}
        />
      )}
      {!client && item.status === "ACCEPTED" && billing?.bill.status==='DEMO_PAID' && (
        <Button
          label="Iniciar servicio"
          busy={busy}
          onPress={() => confirm("¿Iniciar el servicio?", "start")}
        />
      )}
      {client && item.status === "IN_PROGRESS" && billing?.bill.status==='DEMO_PAID' && (
        <Button
          label="Confirmar que el trabajo está terminado"
          busy={busy}
          onPress={() => confirm("¿El servicio está terminado?", "complete")}
        />
      )}
      <EvidencePanel key={id} id={id} session={session} status={item.status} run={run} busy={busy}/>
      {billing && <BillingPanel id={id} session={session} status={item.status} data={billing} busy={busy} run={run} refresh={refresh} />}
      {billing&&['DEMO_PAID','DEMO_REFUNDED'].includes(billing.bill.status)&&<DisputePanel id={id} session={session} run={run} busy={busy} refresh={refresh}/>}
      {rating && (
        <Card>
          <Text style={s.title}>Valoración: {rating.score}/5</Text>
          <Text style={s.body}>
            {rating.comment || "Sin comentario adicional."}
          </Text>
        </Card>
      )}
      {client && item.status === "COMPLETED" && !rating && (
        <Card>
          <Text style={s.title}>¿Cómo estuvo el servicio?</Text>
          <Chips
            items={[1, 2, 3, 4, 5].map((n) => ({ id: n, name: `${n} ★` }))}
            selected={[score]}
            onSelect={setScore}
          />
          <Field
            label="Tu experiencia (opcional)"
            multiline
            value={comment}
            onChangeText={setComment}
          />
          <Button
            label="Enviar valoración"
            busy={busy}
            onPress={() =>
              void act("rating", { score, comment: comment.trim() })
            }
          />
        </Card>
      )}
    </>
  );
}

export function Profile({
  session,
  run,
  busy,
  logout,
  onUser,
}: {
  session: Session;
  run: Run;
  busy: boolean;
  logout: () => void;
  onUser: (user: User) => void;
}) {
  const [personal, setPersonal] = useState(session.user);
  const [personalSaved, setPersonalSaved] = useState(false);
  const [profile, setProfile] = useState<Provider | null>(null);
  const [cats, setCats] = useState<Option[]>([]);
  const [areas, setAreas] = useState<Option[]>([]);
  const [chosenCats, setChosenCats] = useState<number[]>([]);
  const [chosenAreas, setChosenAreas] = useState<number[]>([]);
  const [saved, setSaved] = useState(false);
  const load = () =>
    run(async () => {
      const [p, c, a] = await Promise.all([
        session.user.role === "PROVIDER" ? api<Provider>("auth/me/provider-profile/", session.token) : Promise.resolve(null),
        options("categories/"),
        options("communes/"),
      ]);
      setProfile(p);
      setCats(c);
      setAreas(a);
      setChosenCats(p?.categories.map((v) => v.id) ?? []);
      setChosenAreas(p?.communes.map((v) => v.id) ?? []);
    });
  useEffect(() => {
    void load();
  }, []);
  const toggle = (values: number[], id: number) =>
    values.includes(id) ? values.filter((v) => v !== id) : [...values, id];
  return (
    <>
      <Text style={s.heading}>Tu perfil</Text>
      <Card>
        <Text style={s.title}>
          {session.user.first_name} {session.user.last_name}
        </Text>
        <Text style={s.body}>{session.user.email}</Text>
        <Text style={s.badge}>
          {session.user.role === "CLIENT"
            ? "Cliente"
            : "Prestador de servicios"}
        </Text>
      </Card>
      <Card>
        <Text style={s.title}>Tus datos para próximas solicitudes</Text>
        <Text style={s.body}>Tu dirección se reutiliza al pedir un servicio. Tu teléfono no aparece en el catálogo público.</Text>
        <Field label="Nombre" value={personal.first_name} onChangeText={v => { setPersonalSaved(false); setPersonal({...personal, first_name:v}); }} />
        <Field label="Apellido" value={personal.last_name} onChangeText={v => { setPersonalSaved(false); setPersonal({...personal, last_name:v}); }} />
        <Field label="Teléfono" keyboardType="phone-pad" value={personal.phone ?? ""} onChangeText={v => { setPersonalSaved(false); setPersonal({...personal, phone:v}); }} />
        <Field label="Dirección habitual" value={personal.default_address ?? ""} onChangeText={v => { setPersonalSaved(false); setPersonal({...personal, default_address:v}); }} />
        <Text style={s.label}>Comuna habitual</Text>
        <Chips items={areas} selected={personal.default_commune ? [personal.default_commune] : []} onSelect={v => { setPersonalSaved(false); setPersonal({...personal, default_commune:personal.default_commune === v ? null : v}); }} />
        <Button label="Guardar mis datos" busy={busy} disabled={!personal.first_name.trim() || !personal.last_name.trim()} onPress={() => void run(async () => {
          const user = await api<User>("auth/me/", session.token, "PATCH", {
            first_name: personal.first_name.trim(), last_name: personal.last_name.trim(),
            phone: personal.phone, default_address: personal.default_address, default_commune: personal.default_commune,
          });
          setPersonal(user); onUser(user); setPersonalSaved(true);
        })} />
        {personalSaved && <Text accessibilityLiveRegion="polite" style={s.body}>Datos guardados para tu próxima visita.</Text>}
      </Card>
      {session.user.role === "PROVIDER" && !profile && (
        <Button label="Cargar perfil" busy={busy} onPress={() => void load()} />
      )}
      {profile && (
        <Card>
          <Text style={s.title}>Haz que te encuentren</Text>
          <ProfilePhoto profile={profile} session={session} run={run} busy={busy} onPhoto={avatar=>setProfile(current=>current?{...current,avatar}:current)}/>
          <Text style={s.body}>Selecciona un punto público de atención. Se mostrará a los clientes cuando publiques tu zona; evita indicar tu domicilio privado. No es tu ubicación en tiempo real.</Text>
          <ServiceMap point={profile.latitude != null && profile.longitude != null ? {latitude:profile.latitude,longitude:profile.longitude} : null}
            markers={[]} onPoint={point=>{setSaved(false);setProfile({...profile,...point});}} />
          <Text style={s.body}>{profile.latitude != null ? 'Punto seleccionado. Puedes cambiarlo tocando el mapa.' : 'Toca el mapa para elegir dónde ofreces tus servicios.'}</Text>
          <Button secondary label={profile.map_visible ? 'Ocultar mi punto del mapa' : 'Publicar mi punto en el mapa'}
            onPress={()=>{setSaved(false);setProfile({...profile,map_visible:!profile.map_visible});}} />
          <Text style={s.body}>{profile.map_visible ? 'Zona pública: se publicará al guardar el perfil.' : 'Zona privada: no aparece en el mapa.'}</Text>
          <Field
            label="Nombre visible"
            value={profile.display_name}
            onChangeText={(value) => {
              setSaved(false);
              setProfile({ ...profile, display_name: value });
            }}
          />
          <Field
            label="Sobre tus servicios"
            multiline
            value={profile.description}
            onChangeText={(value) => {
              setSaved(false);
              setProfile({ ...profile, description: value });
            }}
          />
          <Text style={s.label}>Especialidades</Text>
          <Chips
            items={cats}
            selected={chosenCats}
            onSelect={(id) => {
              setSaved(false);
              setChosenCats(toggle(chosenCats, id));
            }}
          />
          <Text style={s.label}>Comunas de atención</Text>
          <Chips
            items={areas}
            selected={chosenAreas}
            onSelect={(id) => {
              setSaved(false);
              setChosenAreas(toggle(chosenAreas, id));
            }}
          />
          <Button
            busy={busy}
            disabled={!profile.display_name.trim()}
            label="Guardar perfil"
            onPress={() =>
              void run(async () => {
                await api("auth/me/provider-profile/", session.token, "PATCH", {
                  display_name: profile.display_name.trim(),
                  description: profile.description.trim(),
                  categories: chosenCats,
                  communes: chosenAreas,
                  latitude: profile.latitude,
                  longitude: profile.longitude,
                  map_visible: profile.map_visible,
                });
                setSaved(true);
              })
            }
          />
          {saved && (
            <Text accessibilityLiveRegion="polite" style={s.body}>
              Perfil guardado correctamente.
            </Text>
          )}
        </Card>
      )}
      {session.user.role === 'CLIENT' && <DemoWallet session={session} run={run} busy={busy}/>}
      <Button
        secondary
        label="Cerrar sesión"
        disabled={busy}
        onPress={logout}
      />
      <Text style={s.body}>
        FIX&GO · Prototipo académico. Los pagos y tarjetas son de demostración, sin cobros reales ni verificación de credenciales profesionales.
      </Text>
    </>
  );
}
