import { useEffect, useRef, useState } from "react";
import { StatusBar } from "expo-status-bar";
import * as SecureStore from "expo-secure-store";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import {
  ActivityIndicator,
  BackHandler,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  Text,
  View,
} from "react-native";
import { api, ApiError, checkHealth, Provider, Session, User } from "./src/api";
import {
  Access,
  Detail,
  Explore,
  NewRequest,
  Profile,
  Requests,
} from "./src/screens";
import { Button, colors, s } from "./src/ui";
import { ProviderHome } from "./src/provider-home";
import { Information } from './src/information';
const SESSION_KEY = "fixgo.session.token";
type Tab = "explore" | "home" | "requests" | "profile" | "information";
type Route =
  | { kind: "new"; provider: Provider }
  | { kind: "detail"; id: number }
  | null;
// Native tokens stay in Keychain/Keystore. Web previews use memory only.
async function saveToken(token: string | null) {
  if (Platform.OS === "web") return;
  if (token) await SecureStore.setItemAsync(SESSION_KEY, token);
  else await SecureStore.deleteItemAsync(SESSION_KEY);
}
function MobileApp() {
  const [session, setSession] = useState<Session | null>(null);
  const [booting, setBooting] = useState(true);
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  const [error, setError] = useState("");
  const [connected, setConnected] = useState(false);
  const [tab, setTab] = useState<Tab>("explore");
  const [route, setRoute] = useState<Route>(null);
  const scroll = useRef<ScrollView>(null);
  async function clearSession() {
    await saveToken(null);
    setSession(null);
    setRoute(null);
  }
  async function run(job: () => Promise<void>) {
    // Lock synchronously: a quick double tap cannot create duplicate requests.
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      await job();
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        try {
          await clearSession();
        } catch {
          setSession(null);
        }
      }
      setError(
        e instanceof Error ? e.message : "No se pudo completar la acción.",
      );
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  useEffect(() => {
    void (async () => {
      try {
        const token =
          Platform.OS === "web"
            ? null
            : await SecureStore.getItemAsync(SESSION_KEY);
        if (token) {
          const user = await api<User>("auth/me/", token);
          setSession({ token, user });
          setTab(user.role === "CLIENT" ? "explore" : "home");
        }
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) await saveToken(null);
        setError(
          e instanceof Error ? e.message : "No se pudo recuperar la sesión.",
        );
      } finally {
        setBooting(false);
      }
    })();
  }, []);
  useEffect(() => {
    const handler = BackHandler.addEventListener("hardwareBackPress", () => {
      if (busy) return true;
      if (route) {
        setRoute(null);
        return true;
      }
      return false;
    });
    return () => handler.remove();
  }, [route, busy]);
  useEffect(() => {
    if (error) scroll.current?.scrollTo({ y: 0, animated: true });
  }, [error]);
  useEffect(() => {
    scroll.current?.scrollTo({ y: 0, animated: false });
  }, [route, tab, session?.user.id]);
  async function onSession(value: Session) {
    await saveToken(value.token);
    setSession(value);
    setTab(value.user.role === "CLIENT" ? "explore" : "home");
    setRoute(null);
  }
  const open = (id: number) => {
    setTab("requests");
    setRoute({ kind: "detail", id });
  };
  const tabs: { id: Tab; label: string; mark: string }[] = [
    ...(session?.user.role === "CLIENT"
      ? [{ id: "explore" as Tab, label: "Explorar", mark: "⌕" }]
      : [{ id: "home" as Tab, label: "Inicio", mark: "⌂" }]),
    { id: "requests", label: "Solicitudes", mark: "≡" },
    { id: "profile", label: "Mi perfil", mark: "○" },
    { id: "information", label: "Información", mark: "i" },
  ];
  return (
    <SafeAreaView style={s.page}>
      <StatusBar style="dark" />
      <View
        style={{
          paddingHorizontal: 22,
          paddingVertical: 14,
          borderBottomWidth: 1,
          borderColor: colors.border,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Text
          accessibilityRole="header"
          style={{ color: colors.ink, fontWeight: "900", fontSize: 25 }}
        >
          FIX<Text style={{ color: "#B67800" }}>&</Text>GO
        </Text>
        <Text style={s.label}>
          {session ? "Santiago, Chile" : "Hecho para tu hogar"}
        </Text>
      </View>
      {booting ? (
        <View
          style={{
            flex: 1,
            justifyContent: "center",
            alignItems: "center",
            gap: 12,
          }}
        >
          <ActivityIndicator color={colors.ink} />
          <Text style={s.body}>Preparando tu sesión…</Text>
        </View>
      ) : (
        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
        >
          <ScrollView
            ref={scroll}
            keyboardShouldPersistTaps="handled"
            contentContainerStyle={session && tab === "explore" && !route ? {flexGrow:1} : s.content}
          >
            {route && (
              <Button
                secondary
                disabled={busy}
                label="‹ Volver"
                onPress={() => {
                  setRoute(null);
                  setError("");
                }}
              />
            )}
            {!!error && (
              <View
                accessibilityRole="alert"
                accessibilityLiveRegion="assertive"
                style={{
                  backgroundColor: "#FCE8E4",
                  padding: 16,
                  borderRadius: 14,
                  gap: 8,
                }}
              >
                <Text style={{ color: "#842E22", lineHeight: 21 }}>
                  {error}
                </Text>
                <Button
                  secondary
                  label="Cerrar aviso"
                  onPress={() => setError("")}
                />
              </View>
            )}
            {busy && (
              <ActivityIndicator
                accessibilityLabel="Cargando"
                color={colors.ink}
              />
            )}
            {!session ? (
              <>
                <Access run={run} busy={busy} onSession={onSession} />
                <Button
                  secondary
                  busy={busy}
                  label="Comprobar conexión"
                  onPress={() =>
                    void run(async () => {
                      await checkHealth();
                      setConnected(true);
                    })
                  }
                />
                {connected && (
                  <Text style={s.body}>
                    Conexión lista. FIX&GO está conectado con el servidor.
                  </Text>
                )}
              </>
            ) : route?.kind === "new" ? (
              <NewRequest
                provider={route.provider}
                session={session}
                run={run}
                busy={busy}
                onCreated={open}
              />
            ) : route?.kind === "detail" ? (
              <Detail
                key={route.id}
                id={route.id}
                session={session}
                run={run}
                busy={busy}
              />
            ) : tab === "explore" ? (
              <Explore
                session={session}
                run={run}
                busy={busy}
                onChoose={(provider) => setRoute({ kind: "new", provider })}
              />
            ) : tab === "information" ? (
              <Information/>
            ) : tab === "home" ? (
              <ProviderHome session={session} run={run} busy={busy} onOpen={open}/>
            ) : tab === "requests" ? (
              <Requests session={session} run={run} busy={busy} onOpen={open} />
            ) : (
              <Profile
                session={session}
                run={run}
                busy={busy}
                onUser={(user) => setSession(current => current ? {...current, user} : current)}
                logout={() =>
                  void run(async () => {
                    try {
                      await api("auth/logout/", session.token, "POST");
                    } finally {
                      // Salir localmente incluso sin red; el token remoto expira a las 24 h.
                      await clearSession();
                    }
                  })
                }
              />
            )}
          </ScrollView>
        </KeyboardAvoidingView>
      )}
      {session && (
        <View
          style={{
            flexDirection: "row",
            backgroundColor: "white",
            borderTopWidth: 1,
            borderColor: colors.border,
            paddingVertical: 8,
          }}
        >
          {tabs.map((t) => (
            <Pressable
              key={t.id}
              disabled={busy}
              accessibilityRole="tab"
              accessibilityState={{ selected: tab === t.id, disabled: busy }}
              onPress={() => {
                setTab(t.id);
                setRoute(null);
                setError("");
              }}
              style={{
                flex: 1,
                alignItems: "center",
                padding: 10,
                gap: 3,
                opacity: busy ? 0.5 : 1,
              }}
            >
              <Text
                style={{
                  color: tab === t.id ? colors.ink : colors.muted,
                  fontWeight: "700",
                  fontSize: 22,
                }}
              >
                {t.mark}
              </Text>
              <Text
                style={{
                  color: tab === t.id ? colors.ink : colors.muted,
                  fontSize: 12,
                  fontWeight: tab === t.id ? "800" : "400",
                }}
              >
                {t.label}
              </Text>
              {tab === t.id && (
                <View
                  style={{
                    width: 20,
                    height: 3,
                    backgroundColor: colors.yellow,
                    borderRadius: 2,
                  }}
                />
              )}
            </Pressable>
          ))}
        </View>
      )}
    </SafeAreaView>
  );
}
export default function App() {
  return (
    <SafeAreaProvider>
      <MobileApp />
    </SafeAreaProvider>
  );
}
