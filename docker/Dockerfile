FROM rust:1.67.1-bullseye AS cargo-c-builder

RUN \
  apt-get update && \
    apt-get install -y musl-tools build-essential

RUN rustup target add x86_64-unknown-linux-musl

RUN cargo install --target=x86_64-unknown-linux-musl  --version 0.9.16 cargo-c --features=vendored-openssl

RUN cargo install av-metrics-tool

# bump: alpine /FROM alpine:([\d.]+)/ docker:alpine|^3
# bump: alpine link "Release notes" https://alpinelinux.org/posts/Alpine-$LATEST-released.html
FROM alpine:3.17.0 AS ffmpeg-builder

RUN apk add --no-cache \
  coreutils \
  wget \
  rust cargo cargo-c \
  openssl-dev openssl-libs-static \
  ca-certificates \
  bash \
  tar \
  build-base \
  autoconf automake \
  libtool \
  diffutils \
  cmake meson ninja \
  git \
  yasm nasm \
  texinfo \
  jq \
  zlib-dev zlib-static \
  bzip2-dev bzip2-static \
  libxml2-dev libxml2-static \
  expat-dev expat-static \
  fontconfig-dev fontconfig-static \
  freetype freetype-dev freetype-static \
  graphite2-static \
  glib-static \
  tiff tiff-dev \
  libjpeg-turbo libjpeg-turbo-dev \
  libpng-dev libpng-static \
  giflib giflib-dev \
  harfbuzz-dev harfbuzz-static \
  fribidi-dev fribidi-static \
  brotli-dev brotli-static \
  soxr-dev soxr-static \
  tcl \
  numactl-dev \
  cunit cunit-dev \
  fftw-dev \
  libsamplerate-dev libsamplerate-static \
  vo-amrwbenc-dev vo-amrwbenc-static \
  snappy snappy-dev snappy-static \
  xxd \
  xz-dev xz-static

# -O3 makes sure we compile with optimization. setting CFLAGS/CXXFLAGS seems to override
# default automake cflags.
# -static-libgcc is needed to make gcc not include gcc_s as "as-needed" shared library which
# cmake will include as a implicit library.
# other options to get hardened build (same as ffmpeg hardened)
ARG CFLAGS="-O3 -s -static-libgcc -fno-strict-overflow -fstack-protector-all -fPIC"
ARG CXXFLAGS="-O3 -s -static-libgcc -fno-strict-overflow -fstack-protector-all -fPIC"
ARG LDFLAGS="-Wl,-z,relro,-z,now"

# retry dns and some http codes that might be transient errors
ARG WGET_OPTS="--retry-on-host-error --retry-on-http-error=429,500,502,503"

# before aom as libvmaf uses it
# bump: vmaf /VMAF_VERSION=([\d.]+)/ https://github.com/Netflix/vmaf.git|*
# bump: vmaf after ./hashupdate Dockerfile VMAF $LATEST
# bump: vmaf link "Release" https://github.com/Netflix/vmaf/releases/tag/v$LATEST
# bump: vmaf link "Source diff $CURRENT..$LATEST" https://github.com/Netflix/vmaf/compare/v$CURRENT..v$LATEST
ARG VMAF_VERSION=2.3.1
ARG VMAF_URL="https://github.com/Netflix/vmaf/archive/refs/tags/v$VMAF_VERSION.tar.gz"
ARG VMAF_SHA256=8d60b1ddab043ada25ff11ced821da6e0c37fd7730dd81c24f1fc12be7293ef2
RUN \
  wget $WGET_OPTS -O vmaf.tar.gz "$VMAF_URL" && \
  echo "$VMAF_SHA256  vmaf.tar.gz" | sha256sum --status -c - && \
  tar xf vmaf.tar.gz && \
  cd vmaf-*/ && cp -r model /usr/share/ && cd libvmaf && meson build --buildtype=release -Ddefault_library=static -Dbuilt_in_models=true -Denable_tests=false -Denable_docs=false -Denable_avx512=true -Denable_float=true && \
  ninja -j$(nproc) -vC build install
# extra libs stdc++ is for vmaf https://github.com/Netflix/vmaf/issues/788
RUN  sed -i 's/-lvmaf /-lvmaf -lstdc++ /' /usr/local/lib/pkgconfig/libvmaf.pc

# build after libvmaf
# bump: aom /AOM_VERSION=([\d.]+)/ git:https://aomedia.googlesource.com/aom|*
# bump: aom after ./hashupdate Dockerfile AOM $LATEST
# bump: aom after COMMIT=$(git ls-remote https://aomedia.googlesource.com/aom v$LATEST^{} | awk '{print $1}') && sed -i -E "s/^ARG AOM_COMMIT=.*/ARG AOM_COMMIT=$COMMIT/" Dockerfile
# bump: aom link "CHANGELOG" https://aomedia.googlesource.com/aom/+/refs/tags/v$LATEST/CHANGELOG
ARG AOM_VERSION=3.5.0
ARG AOM_URL="https://aomedia.googlesource.com/aom"
ARG AOM_COMMIT=bcfe6fbfed315f83ee8a95465c654ee8078dbff9
RUN \
  git clone --depth 1 --branch v$AOM_VERSION "$AOM_URL" && \
  cd aom && test $(git rev-parse HEAD) = $AOM_COMMIT && \
  mkdir build_tmp && cd build_tmp && \
  cmake \
    -G"Unix Makefiles" \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -DENABLE_EXAMPLES=NO \
    -DENABLE_DOCS=NO \
    -DENABLE_TESTS=NO \
    -DENABLE_TOOLS=NO \
    -DCONFIG_TUNE_VMAF=1 \
    -DENABLE_NASM=ON \
    -DCMAKE_INSTALL_LIBDIR=lib \
    .. && \
  make -j$(nproc) install


# bump: dav1d /DAV1D_VERSION=([\d.]+)/ https://code.videolan.org/videolan/dav1d.git|*
# bump: dav1d after ./hashupdate Dockerfile DAV1D $LATEST
# bump: dav1d link "Release notes" https://code.videolan.org/videolan/dav1d/-/tags/$LATEST
ARG DAV1D_VERSION=1.0.0
ARG DAV1D_URL="https://code.videolan.org/videolan/dav1d/-/archive/$DAV1D_VERSION/dav1d-$DAV1D_VERSION.tar.gz"
ARG DAV1D_SHA256=047b8229511a82b5718a1d34c86c067b078efd02f602986d2ed09b23182ec136
RUN \
  wget $WGET_OPTS -O dav1d.tar.gz "$DAV1D_URL" && \
  echo "$DAV1D_SHA256  dav1d.tar.gz" | sha256sum --status -c - && \
  tar xf dav1d.tar.gz && \
  cd dav1d-* && meson build --buildtype release -Ddefault_library=static && \
  ninja -j$(nproc) -C build install

# bump: davs2 /DAVS2_VERSION=([\d.]+)/ https://github.com/pkuvcl/davs2.git|^1
# bump: davs2 after ./hashupdate Dockerfile DAVS2 $LATEST
# bump: davs2 link "Release" https://github.com/pkuvcl/davs2/releases/tag/$LATEST
# bump: davs2 link "Source diff $CURRENT..$LATEST" https://github.com/pkuvcl/davs2/compare/v$CURRENT..v$LATEST
ARG DAVS2_VERSION=1.7
ARG DAVS2_URL="https://github.com/pkuvcl/davs2/archive/refs/tags/$DAVS2_VERSION.tar.gz"
ARG DAVS2_SHA256=b697d0b376a1c7f7eda3a4cc6d29707c8154c4774358303653f0a9727f923cc8
# TODO: seems to be issues with asm on musl
RUN \
  wget $WGET_OPTS -O davs2.tar.gz "$DAVS2_URL" && \
  echo "$DAVS2_SHA256  davs2.tar.gz" | sha256sum --status -c - && \
  tar xf davs2.tar.gz && \
  cd davs2-*/build/linux && ./configure --disable-asm --enable-pic --enable-strip --disable-cli && \
  make -j$(nproc) install

# bump: kvazaar /KVAZAAR_VERSION=([\d.]+)/ https://github.com/ultravideo/kvazaar.git|^2
# bump: kvazaar after ./hashupdate Dockerfile KVAZAAR $LATEST
# bump: kvazaar link "Release notes" https://github.com/ultravideo/kvazaar/releases/tag/v$LATEST
ARG KVAZAAR_VERSION=2.1.0
ARG KVAZAAR_URL="https://github.com/ultravideo/kvazaar/archive/v$KVAZAAR_VERSION.tar.gz"
ARG KVAZAAR_SHA256=bbdd3112182e5660a1c339e30677f871b6eac1e5b4ff1292ee1ae38ecbe11029
RUN \
  wget $WGET_OPTS -O kvazaar.tar.gz "$KVAZAAR_URL" && \
  echo "$KVAZAAR_SHA256  kvazaar.tar.gz" | sha256sum --status -c - && \
  tar xf kvazaar.tar.gz && \
  cd kvazaar-* && ./autogen.sh && ./configure --disable-shared --enable-static && \
  make -j$(nproc) install

# bump: openjpeg /OPENJPEG_VERSION=([\d.]+)/ https://github.com/uclouvain/openjpeg.git|*
# bump: openjpeg after ./hashupdate Dockerfile OPENJPEG $LATEST
# bump: openjpeg link "CHANGELOG" https://github.com/uclouvain/openjpeg/blob/master/CHANGELOG.md
ARG OPENJPEG_VERSION=2.5.0
ARG OPENJPEG_URL="https://github.com/uclouvain/openjpeg/archive/v$OPENJPEG_VERSION.tar.gz"
ARG OPENJPEG_SHA256=0333806d6adecc6f7a91243b2b839ff4d2053823634d4f6ed7a59bc87409122a
RUN \
  wget $WGET_OPTS -O openjpeg.tar.gz "$OPENJPEG_URL" && \
  echo "$OPENJPEG_SHA256  openjpeg.tar.gz" | sha256sum --status -c - && \
  tar xf openjpeg.tar.gz && \
  cd openjpeg-* && mkdir build && cd build && \
  cmake \
    -G"Unix Makefiles" \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -DBUILD_PKGCONFIG_FILES=ON \
    -DBUILD_CODEC=OFF \
    -DWITH_ASTYLE=OFF \
    -DBUILD_TESTING=OFF \
    .. && \
  make -j$(nproc) install

# bump: rav1e /RAV1E_VERSION=([\d.]+)/ https://github.com/xiph/rav1e.git|/\d+\./|*
# bump: rav1e after ./hashupdate Dockerfile RAV1E $LATEST
# bump: rav1e link "Release notes" https://github.com/xiph/rav1e/releases/tag/v$LATEST
# RUSTFLAGS need to fix gcc_s
# https://gitlab.alpinelinux.org/alpine/aports/-/issues/11806
ARG RAV1E_VERSION=0.5.1
ARG RAV1E_URL="https://github.com/xiph/rav1e/archive/v$RAV1E_VERSION.tar.gz"
ARG RAV1E_SHA256=7b3060e8305e47f10b79f3a3b3b6adc3a56d7a58b2cb14e86951cc28e1b089fd
RUN \
  wget $WGET_OPTS -O rav1e.tar.gz "$RAV1E_URL" && \
  echo "$RAV1E_SHA256  rav1e.tar.gz" | sha256sum --status -c - && \
  tar xf rav1e.tar.gz && \
  cd rav1e-* && \
  RUSTFLAGS="-C target-feature=+crt-static" cargo cinstall --release

# bump: svtav1 /SVTAV1_VERSION=([\d.]+)/ https://gitlab.com/AOMediaCodec/SVT-AV1.git|*
# bump: svtav1 after ./hashupdate Dockerfile SVTAV1 $LATEST
# bump: svtav1 link "Release notes" https://gitlab.com/AOMediaCodec/SVT-AV1/-/releases/v$LATEST
ARG SVTAV1_VERSION=1.3.0
ARG SVTAV1_URL="https://gitlab.com/AOMediaCodec/SVT-AV1/-/archive/v$SVTAV1_VERSION/SVT-AV1-v$SVTAV1_VERSION.tar.bz2"
ARG SVTAV1_SHA256=f85fd13ef16880550e425797bdfdf1b0ba310c21d6b343f74ea79dd2fbb2336e
RUN \
  wget $WGET_OPTS -O svtav1.tar.bz2 "$SVTAV1_URL" && \
  echo "$SVTAV1_SHA256  svtav1.tar.bz2" | sha256sum --status -c - && \
  tar xf svtav1.tar.bz2 && \
  cd SVT-AV1-*/Build && \
  cmake \
    -G"Unix Makefiles" \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    .. && \
  make -j$(nproc) install

# has to be before theora
# bump: ogg /OGG_VERSION=([\d.]+)/ https://github.com/xiph/ogg.git|*
# bump: ogg after ./hashupdate Dockerfile OGG $LATEST
# bump: ogg link "CHANGES" https://github.com/xiph/ogg/blob/master/CHANGES
# bump: ogg link "Source diff $CURRENT..$LATEST" https://github.com/xiph/ogg/compare/v$CURRENT..v$LATEST
ARG OGG_VERSION=1.3.5
ARG OGG_URL="https://downloads.xiph.org/releases/ogg/libogg-$OGG_VERSION.tar.gz"
ARG OGG_SHA256=0eb4b4b9420a0f51db142ba3f9c64b333f826532dc0f48c6410ae51f4799b664
RUN \
  wget $WGET_OPTS -O libogg.tar.gz "$OGG_URL" && \
  echo "$OGG_SHA256  libogg.tar.gz" | sha256sum --status -c - && \
  tar xf libogg.tar.gz && \
  cd libogg-* && ./configure --disable-shared --enable-static && \
  make -j$(nproc) install

# bump: theora /THEORA_VERSION=([\d.]+)/ https://github.com/xiph/theora.git|*
# bump: theora after ./hashupdate Dockerfile THEORA $LATEST
# bump: theora link "Release notes" https://github.com/xiph/theora/releases/tag/v$LATEST
# bump: theora link "Source diff $CURRENT..$LATEST" https://github.com/xiph/theora/compare/v$CURRENT..v$LATEST
ARG THEORA_VERSION=1.1.1
ARG THEORA_URL="https://downloads.xiph.org/releases/theora/libtheora-$THEORA_VERSION.tar.bz2"
ARG THEORA_SHA256=b6ae1ee2fa3d42ac489287d3ec34c5885730b1296f0801ae577a35193d3affbc
RUN \
  wget $WGET_OPTS -O libtheora.tar.bz2 "$THEORA_URL" && \
  echo "$THEORA_SHA256  libtheora.tar.bz2" | sha256sum --status -c - && \
  tar xf libtheora.tar.bz2 && \
  # --build=$(arch)-unknown-linux-gnu helps with guessing the correct build. For some reason,
  # build script can't guess the build type in arm64 (hardware and emulated) environment.
  cd libtheora-* && ./configure --build=$(arch)-unknown-linux-gnu --disable-examples --disable-oggtest --disable-shared --enable-static && \
  make -j$(nproc) install

# bump: uavs3d /UAVS3D_COMMIT=([[:xdigit:]]+)/ gitrefs:https://github.com/uavs3/uavs3d.git|re:#^refs/heads/master$#|@commit
# bump: uavs3d after ./hashupdate Dockerfile UAVS3D $LATEST
# bump: uavs3d link "Source diff $CURRENT..$LATEST" https://github.com/uavs3/uavs3d/compare/$CURRENT..$LATEST
ARG UAVS3D_URL="https://github.com/uavs3/uavs3d.git"
ARG UAVS3D_COMMIT=0133ee4b4bbbef7b88802e7ad019b14b9b852c2b
# Removes BIT_DEPTH 10 to be able to build on other platforms. 10 was overkill anyways.
RUN \
  git clone "$UAVS3D_URL" && \
  cd uavs3d && git checkout $UAVS3D_COMMIT && \
#  sed -i 's/define BIT_DEPTH 8/define BIT_DEPTH 10/' source/decore/com_def.h && \
  mkdir build/linux && cd build/linux && \
  cmake \
    -G"Unix Makefiles" \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    ../.. && \
  make -j$(nproc) install

# bump: libvpx /VPX_VERSION=([\d.]+)/ https://github.com/webmproject/libvpx.git|*
# bump: libvpx after ./hashupdate Dockerfile VPX $LATEST
# bump: libvpx link "CHANGELOG" https://github.com/webmproject/libvpx/blob/master/CHANGELOG
# bump: libvpx link "Source diff $CURRENT..$LATEST" https://github.com/webmproject/libvpx/compare/v$CURRENT..v$LATEST
ARG VPX_VERSION=1.12.0
ARG VPX_URL="https://github.com/webmproject/libvpx/archive/v$VPX_VERSION.tar.gz"
ARG VPX_SHA256=f1acc15d0fd0cb431f4bf6eac32d5e932e40ea1186fe78e074254d6d003957bb
RUN \
  wget $WGET_OPTS -O libvpx.tar.gz "$VPX_URL" && \
  echo "$VPX_SHA256  libvpx.tar.gz" | sha256sum --status -c - && \
  tar xf libvpx.tar.gz && \
  cd libvpx-* && ./configure --enable-static --enable-vp9-highbitdepth --disable-shared --disable-unit-tests --disable-examples && \
  make -j$(nproc) install

# bump: libwebp /LIBWEBP_VERSION=([\d.]+)/ https://github.com/webmproject/libwebp.git|*
# bump: libwebp after ./hashupdate Dockerfile LIBWEBP $LATEST
# bump: libwebp link "Release notes" https://github.com/webmproject/libwebp/releases/tag/v$LATEST
# bump: libwebp link "Source diff $CURRENT..$LATEST" https://github.com/webmproject/libwebp/compare/v$CURRENT..v$LATEST
ARG LIBWEBP_VERSION=1.2.4
ARG LIBWEBP_URL="https://github.com/webmproject/libwebp/archive/v$LIBWEBP_VERSION.tar.gz"
ARG LIBWEBP_SHA256=dfe7bff3390cd4958da11e760b65318f0a48c32913e4d5bc5e8d55abaaa2d32e
RUN \
  wget $WGET_OPTS -O libwebp.tar.gz "$LIBWEBP_URL" && \
  echo "$LIBWEBP_SHA256  libwebp.tar.gz" | sha256sum --status -c - && \
  tar xf libwebp.tar.gz && \
  cd libwebp-* && ./autogen.sh && ./configure --disable-shared --enable-static --with-pic --enable-libwebpmux --disable-libwebpextras --disable-libwebpdemux --disable-sdl --disable-gl --disable-png --disable-jpeg --disable-tiff --disable-gif && \
  make -j$(nproc) install

# x264 only have a stable branch no tags and we checkout commit so no hash is needed
# bump: x264 /X264_VERSION=([[:xdigit:]]+)/ gitrefs:https://code.videolan.org/videolan/x264.git|re:#^refs/heads/stable$#|@commit
# bump: x264 after ./hashupdate Dockerfile X264 $LATEST
# bump: x264 link "Source diff $CURRENT..$LATEST" https://code.videolan.org/videolan/x264/-/compare/$CURRENT...$LATEST
ARG X264_URL="https://code.videolan.org/videolan/x264.git"
ARG X264_VERSION=baee400fa9ced6f5481a728138fed6e867b0ff7f
RUN \
  git clone "$X264_URL" && \
  cd x264 && \
  git checkout $X264_VERSION && \
  ./configure --enable-pic --enable-static --disable-cli --disable-lavf --disable-swscale && \
  make -j$(nproc) install

# x265 release is over 1 years old and master branch has a lot of fixes and improvements, so we checkout commit so no hash is needed
# bump: x265 /X265_VERSION=([[:xdigit:]]+)/ gitrefs:https://bitbucket.org/multicoreware/x265_git.git|re:#^refs/heads/master$#|@commit
# bump: x265 after ./hashupdate Dockerfile X265 $LATEST
# bump: x265 link "Source diff $CURRENT..$LATEST" https://bitbucket.org/multicoreware/x265_git/branches/compare/$LATEST..$CURRENT#diff
ARG X265_VERSION=40e37bce9a357fb18f70ff0852015983cf90a6d3
ARG X265_SHA256=069749b97ce9f699cafce0ab3accc199d629bfd0128350348c2f119ca39641c6
ARG X265_URL="https://bitbucket.org/multicoreware/x265_git/get/$X265_VERSION.tar.bz2"
# -w-macro-params-legacy to not log lots of asm warnings
# https://bitbucket.org/multicoreware/x265_git/issues/559/warnings-when-assembling-with-nasm-215
# TODO: remove 'sed' hack when upstream (x265) fixes the issue and adds '-DPIC' to ARM_ARGS
# https://bitbucket.org/multicoreware/x265_git/issues/619/missing-dpic-for-arm-causes-link-error-on
# CMAKEFLAGS issue
# https://bitbucket.org/multicoreware/x265_git/issues/620/support-passing-cmake-flags-to-multilibsh
RUN \
  wget $WGET_OPTS -O x265_git.tar.bz2 "$X265_URL" && \
  echo "$X265_SHA256  x265_git.tar.bz2" | sha256sum --status -c - && \
  tar xf x265_git.tar.bz2 && \
  cd multicoreware-x265_git-*/build/linux && \
  sed -i '/^cmake / s/$/ -G "Unix Makefiles" ${CMAKEFLAGS}/' ./multilib.sh && \
  sed -i 's/ -DENABLE_SHARED=OFF//g' ./multilib.sh && \
  sed -i 's/set(ARM_ARGS -fPIC -flax-vector-conversions)/set(ARM_ARGS -DPIC -fPIC -flax-vector-conversions)/' ../../source/CMakeLists.txt && \
  MAKEFLAGS="-j$(nproc)" \
  CMAKEFLAGS="-DENABLE_SHARED=OFF -DCMAKE_VERBOSE_MAKEFILE=ON -DENABLE_AGGRESSIVE_CHECKS=ON -DCMAKE_ASM_NASM_FLAGS=-w-macro-params-legacy -DENABLE_NASM=ON -DCMAKE_BUILD_TYPE=Release" \
  ./multilib.sh && \
  make -C 8bit -j$(nproc) install

# http://websvn.xvid.org/cvs/viewvc.cgi/trunk/xvidcore/build/generic/configure.in?revision=2146&view=markup
# bump: xvid /XVID_VERSION=([\d.]+)/ svn:http://anonymous:@svn.xvid.org|/^release-(.*)$/|/_/./|^1
# bump: xvid after ./hashupdate Dockerfile XVID $LATEST
# add extra CFLAGS that are not enabled by -O3
ARG XVID_VERSION=1.3.7
ARG XVID_URL="https://downloads.xvid.com/downloads/xvidcore-$XVID_VERSION.tar.gz"
ARG XVID_SHA256=abbdcbd39555691dd1c9b4d08f0a031376a3b211652c0d8b3b8aa9be1303ce2d
RUN \
  wget $WGET_OPTS -O libxvid.tar.gz "$XVID_URL" && \
  echo "$XVID_SHA256  libxvid.tar.gz" | sha256sum --status -c - && \
  tar xf libxvid.tar.gz && \
  cd xvidcore/build/generic && \
  CFLAGS="$CFLAGS -fstrength-reduce -ffast-math" ./configure && \
  make -j$(nproc) && make install

# bump: zimg /ZIMG_VERSION=([\d.]+)/ https://github.com/sekrit-twc/zimg.git|*
# bump: zimg after ./hashupdate Dockerfile ZIMG $LATEST
# bump: zimg link "ChangeLog" https://github.com/sekrit-twc/zimg/blob/master/ChangeLog
ARG ZIMG_VERSION=3.0.4
ARG ZIMG_URL="https://github.com/sekrit-twc/zimg/archive/release-$ZIMG_VERSION.tar.gz"
ARG ZIMG_SHA256=219d1bc6b7fde1355d72c9b406ebd730a4aed9c21da779660f0a4c851243e32f
RUN \
  wget $WGET_OPTS -O zimg.tar.gz "$ZIMG_URL" && \
  echo "$ZIMG_SHA256  zimg.tar.gz" | sha256sum --status -c - && \
  tar xf zimg.tar.gz && \
  cd zimg-* && ./autogen.sh && ./configure --disable-shared --enable-static && \
  make -j$(nproc) install

# bump: ffmpeg /FFMPEG_VERSION=([\d.]+)/ https://github.com/FFmpeg/FFmpeg.git|^5
# bump: ffmpeg after ./hashupdate Dockerfile FFMPEG $LATEST
# bump: ffmpeg link "Changelog" https://github.com/FFmpeg/FFmpeg/blob/n$LATEST/Changelog
# bump: ffmpeg link "Source diff $CURRENT..$LATEST" https://github.com/FFmpeg/FFmpeg/compare/n$CURRENT..n$LATEST
ARG FFMPEG_VERSION=5.1.2
ARG FFMPEG_URL="https://ffmpeg.org/releases/ffmpeg-$FFMPEG_VERSION.tar.bz2"
ARG FFMPEG_SHA256=39a0bcc8d98549f16c570624678246a6ac736c066cebdb409f9502e915b22f2b
# sed changes --toolchain=hardened -pie to -static-pie
# extra ldflags stack-size=2097152 is to increase default stack size from 128KB (musl default) to something
# more similar to glibc (2MB). This fixing segfault with libaom-av1 and libsvtav1 as they seems to pass
# large things on the stack.
RUN \
  wget $WGET_OPTS -O ffmpeg.tar.bz2 "$FFMPEG_URL" && \
  echo "$FFMPEG_SHA256  ffmpeg.tar.bz2" | sha256sum --status -c - && \
  tar xf ffmpeg.tar.bz2 && \
  cd ffmpeg-* && \
  sed -i 's/add_ldexeflags -fPIE -pie/add_ldexeflags -fPIE -static-pie/' configure && \
  ./configure \
  --pkg-config-flags="--static" \
  --extra-cflags="-fopenmp" \
  --extra-ldflags="-fopenmp -Wl,-z,stack-size=2097152" \
  --toolchain=hardened \
  --disable-debug \
  --disable-shared \
  --disable-ffplay \
  --enable-static \
  --enable-gpl \
  --enable-version3 \
  --enable-nonfree \
  --enable-fontconfig \
  --enable-gray \
  --enable-iconv \
  --enable-libaom \
  --enable-libdav1d \
  --enable-libdavs2 \
  --enable-libfreetype \
  --enable-libfribidi \
  --enable-libkvazaar \
  --enable-libopenjpeg \
  --enable-librav1e \
  --enable-libsnappy \
  --enable-libsoxr \
  --enable-libsvtav1 \
  --enable-libtheora \
  --enable-libuavs3d \
  --enable-libvmaf \
  --enable-libvo-amrwbenc \
  --enable-libvpx \
  --enable-libwebp \
  --enable-libx264 \
  --enable-libx265 \
  --enable-libxml2 \
  --enable-libxvid \
  --enable-libzimg \
  --enable-openssl \
  || (cat ffbuild/config.log ; false) \
  && make -j$(nproc) install

RUN \
  EXPAT_VERSION=$(pkg-config --modversion expat) \
  FFTW_VERSION=$(pkg-config --modversion fftw3) \
  FONTCONFIG_VERSION=$(pkg-config --modversion fontconfig)  \
  FREETYPE_VERSION=$(pkg-config --modversion freetype2)  \
  FRIBIDI_VERSION=$(pkg-config --modversion fribidi)  \
  LIBSAMPLERATE_VERSION=$(pkg-config --modversion samplerate) \
  LIBXML2_VERSION=$(pkg-config --modversion libxml-2.0) \
  OPENSSL_VERSION=$(pkg-config --modversion openssl) \
  SOXR_VERSION=$(pkg-config --modversion soxr) \
  LIBVO_AMRWBENC_VERSION=$(pkg-config --modversion vo-amrwbenc) \
  SNAPPY_VERSION=$(apk info -a snappy | head -n1 | awk '{print $1}' | sed -e 's/snappy-//') \
  jq -n \
  '{ \
  expat: env.EXPAT_VERSION, \
  ffmpeg: env.FFMPEG_VERSION, \
  fftw: env.FFTW_VERSION, \
  fontconfig: env.FONTCONFIG_VERSION, \
  libaom: env.AOM_VERSION, \
  libdav1d: env.DAV1D_VERSION, \
  libdavs2: env.DAVS2_VERSION, \
  libfreetype: env.FREETYPE_VERSION, \
  libfribidi: env.FRIBIDI_VERSION, \
  libkvazaar: env.KVAZAAR_VERSION, \
  libogg: env.OGG_VERSION, \
  libopenjpeg: env.OPENJPEG_VERSION, \
  libopus: env.OPUS_VERSION, \
  librav1e: env.RAV1E_VERSION, \
  libsamplerate: env.LIBSAMPLERATE_VERSION, \
  libsoxr: env.SOXR_VERSION, \
  libsnappy: env.SNAPPY_VERSION, \
  libsvtav1: env.SVTAV1_VERSION, \
  libtheora: env.THEORA_VERSION, \
  libuavs3d: env.UAVS3D_COMMIT, \
  libvmaf: env.VMAF_VERSION, \
  libvo_amrwbenc: env.LIBVO_AMRWBENC_VERSION, \
  libvpx: env.VPX_VERSION, \
  libwebp: env.LIBWEBP_VERSION, \
  libx264: env.X264_VERSION, \
  libx265: env.X265_VERSION, \
  libxml2: env.LIBXML2_VERSION, \
  libxvid: env.XVID_VERSION, \
  libzimg: env.ZIMG_VERSION, \
  openssl: env.OPENSSL_VERSION, \
  }' > /versions.json

# make sure binaries has no dependencies, is relro, pie and stack nx
COPY checkelf /
RUN \
  /checkelf /usr/local/bin/ffmpeg && \
  /checkelf /usr/local/bin/ffprobe


# Compile VMAF
FROM python:3.8-slim as vmaf-builder

COPY --from=ffmpeg-builder /vmaf-* /vmaf/

RUN \
  apt update -y && \
  apt-get install -y --no-install-recommends build-essential gcc nasm doxygen python3-dev libsvm-dev && \
  cd vmaf/ && \
  pip3 install cython numpy meson ninja && \
  pip3 install -r python/requirements.txt && \
  make clean; make


FROM ubuntu:jammy as vqm-metric

ENV DEBIAN_FRONTEND=noninteractive

# Install vqmetric VQM
RUN apt-get update -y && \
   apt install -y make cmake g++ libopencv-dev git ca-certificates --no-install-recommends

RUN cd / && \
  git clone https://github.com/grishnagkh/vqmetric.git && \
  cd vqmetric/ && make && \
  make install

# Build final image with Jupyter Notebook
# copying artifacts from the intermediate containers
FROM jupyter/base-notebook:ubuntu-22.04

USER root

COPY --from=ffmpeg-builder /versions.json /usr/local/bin/ffmpeg /usr/local/bin/ffprobe /usr/bin/
COPY --from=ffmpeg-builder /usr/local/share/doc/ffmpeg/* /doc/
COPY --from=ffmpeg-builder /etc/ssl/cert.pem /etc/ssl/cert.pem
COPY --from=vmaf-builder /vmaf /vmaf/
COPY --from=vqm-metric /usr/bin/vqtool /usr/bin/
COPY --from=cargo-c-builder /usr/local/cargo/bin/av-metrics-tool /usr/bin/
COPY requirements.txt /

RUN chown jovyan:users -R /vmaf/*
RUN pip install --no-cache-dir -r /requirements.txt

RUN \
  apt-get update -y && \
  apt-get install -y --no-install-recommends ca-certificates git curl && \
  apt-get install -y python2

RUN \
  cd / && \
  curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py && \
  python2.7 get-pip.py && \
  rm get-pip.py && \
  pip2 install virtualenv  && \
  mkdir scikitvenv && \
  chown jovyan:users -R /scikitvenv

USER jovyan

# Install kernel for Scikit-Video
RUN \
   python2.7 -m virtualenv /scikitvenv --system-site-packages && \
   source /scikitvenv/bin/activate && \
   pip install scikit-video pandas && \
   pip install ipykernel && \
   python2.7 -m ipykernel install --user --name=Scikit-Video


USER root

RUN apt-get install -y --no-install-recommends bc jq libopencv-dev

# Copy videos, scripts, notebooks and results to image
RUN mkdir -p /home/jovyan/work/examples && \
    mkdir /scripts

COPY examples /home/jovyan/work/examples
COPY scripts/vqmcli /usr/local/bin
COPY scripts/scikit_metric.py scripts/format_results.py  /scripts/

RUN chown jovyan:users -R /home/jovyan/work/examples && \
    chmod a+x /usr/local/bin/vqmcli && \
    chmod a+x /scripts/scikit_metric.py && \
    chmod a+x /scripts/format_results.py

EXPOSE 8050 8888

USER jovyan
