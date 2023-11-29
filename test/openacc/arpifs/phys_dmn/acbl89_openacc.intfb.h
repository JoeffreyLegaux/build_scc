INTERFACE
  SUBROUTINE ACBL89_OPENACC (YDCST, YDPHY, YDPHY0, KIDIA, KFDIA, KLON, KTDIAN, KLEV, PAPHI, PAPHIF, PAPRS, PAPRSF, PT, PECT,  &
  & PQV, PQICE, PQLI, PNLAB, PNLABCVP, PGZ0, PTS, PUSLE, PLMECT, PPHI3, YDSTACK)
!$acc routine( ACBL89_OPENACC ) seq
    
    USE PARKIND1, ONLY: JPIM, JPRB
    USE YOMHOOK, ONLY: LHOOK, DR_HOOK, JPHOOK
    
    USE YOMCST, ONLY: TCST
    USE YOMPHY, ONLY: TPHY
    USE YOMPHY0, ONLY: TPHY0
    
    !-----------------------------------------------------------------------
    
    USE STACK_MOD
    
    IMPLICIT NONE
    
    TYPE(TCST), INTENT(IN) :: YDCST
    TYPE(TPHY), INTENT(IN) :: YDPHY
    TYPE(TPHY0), INTENT(IN) :: YDPHY0
    INTEGER(KIND=JPIM), INTENT(IN) :: KLON
    INTEGER(KIND=JPIM), INTENT(IN) :: KLEV
    INTEGER(KIND=JPIM), INTENT(IN) :: KIDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KFDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KTDIAN
    REAL(KIND=JPRB), INTENT(IN) :: PNLAB(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PNLABCVP(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PAPHI(KLON, 0:KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PAPHIF(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PAPRS(KLON, 0:KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PAPRSF(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PT(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PECT(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PQV(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PQICE(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PQLI(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PGZ0(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PTS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PUSLE(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(OUT) :: PLMECT(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(OUT) :: PPHI3(KLON, KLEV)
    
    !-----------------------------------------------------------------------
    
    
    
    ! Tableaux pour les sorties sur listing (1D seulement)
    
    
    TYPE(STACK), INTENT(IN) :: YDSTACK
  END SUBROUTINE ACBL89_OPENACC
END INTERFACE
