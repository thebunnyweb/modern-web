import { useAuth } from "react-oidc-context";
import { useEffect, useMemo } from "react";
import { WebStorageStateStore } from "oidc-client-ts"; // optional (see #4)

export default function App() {
  const auth = useAuth();

  const isCallback = useMemo(
    () => /[?&](code|error)=/.test(window.location.search),
    []
  );

  // Do NOT auto signinSilent() on mount; let automaticSilentRenew handle it.

  // 3a) Finish the redirect once
  useEffect(() => {
    if (isCallback) {
      auth.signinRedirectCallback()
        .finally(() => {
          // strip ?code=…&state=… from URL to avoid loops
          window.history.replaceState({}, document.title, window.location.pathname);
        });
    }
  }, [isCallback]);

  // 3b) (Optional) Auto-kick login in TEST only, otherwise show a button
  useEffect(() => {
    if (process.env.REACT_APP_ENV === "test" &&
        !isCallback &&
        !auth.isAuthenticated &&
        !auth.isLoading &&
        !auth.activeNavigator &&   // prevents repeat redirects
        !auth.error) {
      // If you want the form to appear automatically in TEST:
      // auth.signinRedirect();
    }
  }, [auth.isAuthenticated, auth.isLoading, auth.activeNavigator, auth.error, isCallback]);

  if (!auth.isAuthenticated) {
    return (
      <button onClick={() => auth.signinRedirect()}>
        Sign in
      </button>
    );
  }

  return <YourRealApp />;
}