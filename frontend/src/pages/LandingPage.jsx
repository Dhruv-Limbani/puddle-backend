import React, { useRef, useMemo, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'
import * as THREE from 'three'
import gsap from 'gsap'
import { useNavigate } from 'react-router-dom'
import './LandingPage.css'

// Vertex Shader
const vertexShader = `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`

// Fragment Shader (Dither + Noise + Gradient)
const fragmentShader = `
uniform float uTime;
uniform vec2 uResolution;
varying vec2 vUv;

// Simplex 2D noise
vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }
float snoise(vec2 v){
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
           -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy) );
  vec2 x0 = v -   i + dot(i, C.xx);
  vec2 i1;
  i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
  + i.x + vec3(0.0, i1.x, 1.0 ));
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
  m = m*m ;
  m = m*m ;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
  vec3 g;
  g.x  = a0.x  * x0.x  + h.x  * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}

void main() {
  vec2 uv = vUv;
  
  // Slow moving noise
  float noiseVal = snoise(uv * 3.0 + uTime * 0.2);
  
  // Color Gradient (Blue/Purple/Teal)
  vec3 color1 = vec3(0.1, 0.1, 0.3); // Dark Blue
  vec3 color2 = vec3(0.5, 0.2, 0.8); // Purple
  vec3 color3 = vec3(0.0, 0.8, 0.8); // Cyan
  
  vec3 baseColor = mix(color1, color2, uv.y + noiseVal * 0.2);
  baseColor = mix(baseColor, color3, sin(uTime * 0.5 + uv.x * 5.0) * 0.2);
  
  // Dither Effect
  float dither = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
  vec3 finalColor = baseColor + (dither * 0.1 - 0.05); // Add slight noise
  
  // Quantize colors for retro feel
  float steps = 8.0;
  finalColor = floor(finalColor * steps) / steps;

  gl_FragColor = vec4(finalColor, 1.0);
}
`

const DitherSphere = () => {
  const meshRef = useRef()
  
  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uResolution: { value: new THREE.Vector2(
        typeof window !== 'undefined' ? window.innerWidth : 0,
        typeof window !== 'undefined' ? window.innerHeight : 0
      ) }
    }),
    []
  )

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.material.uniforms.uTime.value = state.clock.getElapsedTime()
      meshRef.current.rotation.y += 0.002
      meshRef.current.rotation.x += 0.001
    }
  })

  return (
    <mesh ref={meshRef} scale={2.5}>
      <sphereGeometry args={[1, 128, 128]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        wireframe={false}
      />
    </mesh>
  )
}

const HeroContent = () => {
  const navigate = useNavigate()
  const titleRef = useRef()
  const textRef = useRef()
  const btnRef = useRef()

  useEffect(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
    tl.fromTo(titleRef.current, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 1, delay: 0.5 })
      .fromTo(textRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1 }, '-=0.5')
      .fromTo(btnRef.current, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.5 }, '-=0.5')
  }, [])

  return (
    <div className="hero-overlay">
      <div className="hero-content">
        <h1 ref={titleRef} className="hero-title">
          PUDDLE <span className="highlight">AI</span>
        </h1>
        <p ref={textRef} className="hero-subtitle">
          The future of dataset marketplaces. Powered by Liquid Intelligence.
        </p>
        <div ref={btnRef} className="hero-actions">
          <button className="cta-button primary" onClick={() => navigate('/login')}>
            Enter Portal
          </button>
          <button className="cta-button secondary" onClick={() => navigate('/signup')}>
            Initialize
          </button>
        </div>
      </div>
    </div>
  )
}

export default function LandingPage() {
  return (
    <div className="landing-page-container">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <color attach="background" args={['#050505']} />
        <ambientLight intensity={0.5} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <DitherSphere />
        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
      </Canvas>
      <HeroContent />
    </div>
  )
}

