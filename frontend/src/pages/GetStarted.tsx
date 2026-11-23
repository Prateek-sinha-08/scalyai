import { GetStartedProvider, useGetStarted } from "@/components/get-started/get-started-context"
import { GetStartedForm } from "@/components/get-started/get-started-form"
import { PhaseExtracting } from "@/components/get-started/phase-extracting"
import { PhaseForm } from "@/components/get-started/phase-form"

function PhaseRouter() {
  const { phase } = useGetStarted()
  return (
    <>
      {phase === "upload" && <GetStartedForm />}
      {phase === "extracting" && <PhaseExtracting />}
      {phase === "form" && <PhaseForm />}
    </>
  )
}

export default function GetStarted() {
  return (
    <div className="w-full max-w-xl">
        <GetStartedProvider>
          <PhaseRouter />
        </GetStartedProvider>
    </div>
  )
}
