# 🔄 Auto-Update 설정 가이드

## 🎯 Auto-Update 활성화 방법

### 1️⃣ 애드온 설정에서 Auto-update 켜기

1. **설정 → 애드온 → Kocom Wallpad**
2. **Info 탭** 상단
3. **"Auto update"** 토글 ON 🔄
4. 저장

### 2️⃣ 작동 원리

- **매일 자동 체크**: Home Assistant가 하루에 한 번 업데이트 확인
- **자동 설치**: 새 버전 발견 시 자동으로 업데이트 및 재시작
- **안정성**: `stage: stable` 표시된 버전만 자동 업데이트

## ⚙️ 수동 업데이트 체크

즉시 업데이트 확인하려면:

1. **애드온 스토어 → ⋮ → Reload**
2. **Kocom Wallpad 애드온 → Update** (있으면 표시)

## 📊 업데이트 확인

### 현재 버전 확인
- 애드온 Info 탭에서 Version 확인
- 현재: **2025.01.009**

### 업데이트 로그
- 설정 → 시스템 → 로그
- Supervisor 로그에서 업데이트 기록 확인

## 🚨 주의사항

### Auto-update가 작동하지 않는 경우:

1. **GitHub 저장소 문제**
   - 인터넷 연결 확인
   - GitHub 접근 가능 여부 확인

2. **버전 번호 형식**
   - 반드시 증가하는 버전 번호 필요
   - 예: 2025.01.009 → 2025.01.010

3. **Supervisor 재시작**
   ```yaml
   ha supervisor restart
   ```

## 🔧 문제 해결

### Auto-update 비활성화 방법
안정성 문제가 있을 경우:
1. Info 탭 → Auto update OFF
2. 수동으로만 업데이트

### 특정 버전 고정
```yaml
# configuration.yaml에 추가 (권장하지 않음)
hassio:
  addon_update_strategy: "manual"
```

## 📝 업데이트 내역 확인

- GitHub Releases: https://github.com/Hyunki6040/kocom.py/releases
- Commit 내역: https://github.com/Hyunki6040/kocom.py/commits/master

## ✅ Auto-update 장점

1. **자동화**: 수동 업데이트 불필요
2. **최신 기능**: 버그 수정 및 개선사항 즉시 적용
3. **안정성**: stable 버전만 자동 적용

## ⚠️ 백업 권장

Auto-update 활성화 전:
- 설정 → 시스템 → 백업 → 새 백업 생성

---

**현재 상태**: 
- ✅ Auto-update 지원 추가됨 (v2025.01.009)
- ✅ GitHub Actions 자동 릴리스 설정
- ✅ 안정적인 버전 관리 시스템